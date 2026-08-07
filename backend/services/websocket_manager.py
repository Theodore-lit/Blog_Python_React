"""
WebSocketManager — gestionnaire centralisé des connexions WebSocket actives.

Responsabilités UNIQUES de ce module :
  - Maintenir un registre des sockets actifs, indexé par post_id (canaux "rooms")
    et par user_id (notifications personnelles).
  - Exposer des méthodes de connexion / déconnexion / diffusion.

Ce module ne contient AUCUNE logique métier.
Toute décision d'envoyer un message doit venir de la couche Action.
"""

import asyncio
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Registre thread-safe (mono-process asyncio) des connexions WebSocket.

    Registres :
        _post_connections  : dict[post_id, set[WebSocket]]
            → tous les clients qui consultent actuellement la page d'un post.
        _user_connections  : dict[user_id, set[WebSocket]]
            → toutes les connexions actives d'un utilisateur donné
              (un même user peut avoir plusieurs onglets ouverts).
    """

    def __init__(self) -> None:
        # post_id → ensemble de sockets qui « regardent » ce post
        self._post_connections: dict[int, set[WebSocket]] = defaultdict(set)
        # user_id → ensemble de sockets appartenant à cet utilisateur
        self._user_connections: dict[int, set[WebSocket]] = defaultdict(set)

    # ------------------------------------------------------------------
    # Connexion / déconnexion
    # ------------------------------------------------------------------

    async def connect(
        self,
        websocket: WebSocket,
        post_id: int,
        user_id: int,
    ) -> None:
        """
        Enregistre une nouvelle connexion dans les deux registres.
        websocket.accept() doit avoir été appelé AVANT cette méthode.
        """
        self._post_connections[post_id].add(websocket)
        self._user_connections[user_id].add(websocket)
        logger.debug(
            "WebSocket connected — user_id=%s post_id=%s  "
            "(post_sockets=%s)",
            user_id,
            post_id,
            len(self._post_connections[post_id]),
        )

    def disconnect(
        self,
        websocket: WebSocket,
        post_id: int,
        user_id: int,
    ) -> None:
        """
        Retire la connexion des deux registres.
        Nettoie les entrées vides pour éviter les fuites mémoire.
        """
        self._post_connections[post_id].discard(websocket)
        if not self._post_connections[post_id]:
            del self._post_connections[post_id]

        self._user_connections[user_id].discard(websocket)
        if not self._user_connections[user_id]:
            del self._user_connections[user_id]

        logger.debug(
            "WebSocket disconnected — user_id=%s post_id=%s",
            user_id,
            post_id,
        )

    # ------------------------------------------------------------------
    # Diffusion
    # ------------------------------------------------------------------

    async def broadcast_to_post(self, post_id: int, message: dict) -> None:
        """
        Envoie `message` (sérialisé en JSON) à tous les clients connectés
        sur le canal du post `post_id`.

        Les sockets dont l'envoi échoue sont silencieusement ignorés :
        c'est la déconnexion naturelle qui nettoie le registre.
        """
        sockets = list(self._post_connections.get(post_id, set()))
        if not sockets:
            return

        tasks = [_safe_send(ws, message) for ws in sockets]
        await asyncio.gather(*tasks)
        logger.debug(
            "broadcast_to_post — post_id=%s  recipients=%s  type=%s",
            post_id,
            len(sockets),
            message.get("type"),
        )

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """
        Envoie `message` à toutes les connexions actives de l'utilisateur
        `user_id` (notifications personnelles).
        """
        sockets = list(self._user_connections.get(user_id, set()))
        if not sockets:
            return

        tasks = [_safe_send(ws, message) for ws in sockets]
        await asyncio.gather(*tasks)
        logger.debug(
            "send_to_user — user_id=%s  connections=%s  type=%s",
            user_id,
            len(sockets),
            message.get("type"),
        )

    # ------------------------------------------------------------------
    # Introspection (utile pour les tests / health checks)
    # ------------------------------------------------------------------

    def connected_to_post(self, post_id: int) -> int:
        """Nombre de clients connectés sur le canal d'un post."""
        return len(self._post_connections.get(post_id, set()))

    def connected_as_user(self, user_id: int) -> int:
        """Nombre de connexions actives pour un utilisateur donné."""
        return len(self._user_connections.get(user_id, set()))


# ---------------------------------------------------------------------------
# Helper interne
# ---------------------------------------------------------------------------

async def _safe_send(websocket: WebSocket, message: dict) -> None:
    """Tente d'envoyer un message JSON ; avale l'exception en cas d'échec."""
    try:
        await websocket.send_json(message)
    except Exception as exc:  # noqa: BLE001
        logger.debug("_safe_send failed (socket likely closed): %s", exc)


# ---------------------------------------------------------------------------
# Instance singleton — importée par les Actions et l'endpoint WS
# ---------------------------------------------------------------------------

manager = WebSocketManager()
