"""
Routes WebSocket :
  WS /api/ws/posts/{post_id}  — canal temps réel d'un post (commentaires, likes)

Conventions :
  - websocket.accept() est appelé UNIQUEMENT après validation du JWT.
  - Si le token est absent ou invalide, get_current_user_ws ferme la connexion
    avec le code 4401 et retourne None — l'endpoint retourne immédiatement.
  - La vérification que le post existe passe par PostRepository
    (aucun accès direct à la DB dans ce fichier).
  - Aucune logique d'émission d'événements ici : les Actions s'en chargent.
"""

import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middlewares.auth_middleware import get_current_user_ws
from app.models.user import User
from app.repositories.post_repository import PostRepository
from services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

# Code WebSocket applicatif : post introuvable (équivalent HTTP 404)
WS_CLOSE_NOT_FOUND = 4404


@router.websocket("/api/ws/posts/{post_id}")
async def ws_post_channel(
    websocket: WebSocket,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_ws),
) -> None:
    """
    Canal WebSocket d'un post.

    Cycle de vie :
      1. get_current_user_ws valide le JWT (query param ?token=).
         → Échec : connexion déjà fermée par la dépendance, on retourne.
      2. Vérification de l'existence du post via PostRepository.
         → Post introuvable : fermeture avec code 4404.
      3. websocket.accept() — handshake WebSocket complété.
      4. Enregistrement dans le manager (canal post_id + canal user_id).
      5. Boucle de réception : maintient la connexion ouverte.
         Les messages entrants du client sont ignorés (canal read-only côté serveur) ;
         la boucle sert uniquement à détecter la déconnexion.
      6. WebSocketDisconnect → désenregistrement propre du manager.

    Paramètre query obligatoire :
        token (str) — JWT obtenu via POST /api/auth/login
    """
    # --- Étape 1 : Auth ---
    # get_current_user_ws a déjà fermé la socket si le token est invalide/absent
    if current_user is None:
        return

    # --- Étape 2 : Vérification post (via Repository — pas d'accès DB direct) ---
    repo = PostRepository(db)
    post = repo.get_by_id(post_id)
    if post is None:
        await websocket.close(code=WS_CLOSE_NOT_FOUND)
        logger.debug("ws_post_channel — post %s not found, closed 4404", post_id)
        return

    # --- Étape 3 : Acceptation du handshake ---
    await websocket.accept()

    # --- Étape 4 : Enregistrement dans le manager ---
    await manager.connect(websocket, post_id=post_id, user_id=current_user.id)
    logger.info(
        "WS connected — user_id=%s post_id=%s",
        current_user.id,
        post_id,
    )

    # --- Étape 5 : Boucle de maintien de connexion ---
    try:
        while True:
            # On attend des messages du client pour détecter la déconnexion.
            # Ce canal est en lecture seule côté serveur : les messages entrants
            # sont intentionnellement ignorés (le client ne doit pas envoyer de données).
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        # --- Étape 6 : Nettoyage ---
        manager.disconnect(websocket, post_id=post_id, user_id=current_user.id)
        logger.info(
            "WS disconnected — user_id=%s post_id=%s",
            current_user.id,
            post_id,
        )
