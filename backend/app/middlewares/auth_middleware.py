"""
auth_middleware.py — Dépendances FastAPI pour l'authentification JWT.

Fonctions exportées :
    get_current_user(token, db)      → Depends() pour les routes HTTP classiques.
    get_current_user_ws(token, db)   → Depends() pour les endpoints WebSocket
                                       (lit le token depuis le query param ?token=).

Ce module est le SEUL endroit où le token JWT est décodé.
Aucune route ne doit vérifier un token manuellement dans son corps.

Conventions de sécurité :
  - On ne logue JAMAIS le contenu du token.
  - On ne retourne JAMAIS hashed_password dans cet objet.
"""

from fastapi import Depends, HTTPException, Query, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

# tokenUrl pointe vers l'endpoint de login — utilisé par Swagger UI pour le bouton Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalide ou expiré.",
    headers={"WWW-Authenticate": "Bearer"},
)

# Code WebSocket 4401 : convention communautaire pour "Unauthorized" sur WS
# (4000-4999 sont réservés à l'application par la spec RFC 6455)
WS_CLOSE_UNAUTHORIZED = 4401


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _decode_token(token: str) -> int:
    """
    Décode un JWT et retourne le user_id (claim `sub` converti en int).
    Lève HTTP 401 si le token est invalide, expiré, ou si `sub` est absent.

    Réutilisé par get_current_user (HTTP) et get_current_user_ws (WebSocket).
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise CREDENTIALS_EXCEPTION
        return int(user_id)
    except JWTError:
        raise CREDENTIALS_EXCEPTION


def _load_user(user_id: int, db: Session) -> User:
    """
    Charge l'utilisateur depuis le Repository.
    Lève HTTP 401 si l'utilisateur n'existe plus en base.
    """
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


# ---------------------------------------------------------------------------
# Dépendance HTTP (routes classiques)
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Depends() pour les routes HTTP protégées.
    Le token est extrait automatiquement depuis l'en-tête Authorization: Bearer <token>.
    """
    user_id = _decode_token(token)
    return _load_user(user_id, db)


# ---------------------------------------------------------------------------
# Dépendance WebSocket
# ---------------------------------------------------------------------------

async def get_current_user_ws(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Depends() pour les endpoints WebSocket.

    Le token JWT doit être transmis en query param :
        ws://host/api/ws/posts/42?token=<jwt>

    Pourquoi un query param et non un header ?
    Les headers custom (Authorization: Bearer …) ne sont pas garantis sur tous
    les clients WebSocket natifs, notamment React Native. Le query param est le
    moyen portable recommandé pour ce contexte.

    Comportement :
      - Token absent ou invalide → ferme la connexion WS avec le code 4401
        et retourne None (l'endpoint doit retourner immédiatement après).
      - Token valide → retourne l'objet User.

    Note : websocket.close() est appelé ici mais websocket.accept() ne l'a pas
    encore été — FastAPI gère correctement ce cas (envoi d'un Close frame avant
    le handshake HTTP→WS est traduit en réponse HTTP 403 par Starlette).
    """
    if token is None:
        await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
        return None

    try:
        user_id = _decode_token(token)
        return _load_user(user_id, db)
    except HTTPException:
        await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
        return None
