# Blog API — Documentation backend

> FastAPI · SQLAlchemy · PostgreSQL · WebSocket

---

## Table des matières

1. [WebSocket Manager](#1-websocket-manager)
2. [Authentification WebSocket](#2-authentification-websocket)
3. [Endpoint WebSocket](#3-endpoint-websocket)
4. [Branchement des Actions (diffusion temps réel)](#4-branchement-des-actions)
5. [Enregistrement du router](#5-enregistrement-du-router)

---

## 1. WebSocket Manager

**Fichier :** `services/websocket_manager.py`

### Ce qui a été ajouté

Gestionnaire centralisé des connexions WebSocket actives. Il expose un singleton `manager` importable partout dans le projet.

**Registres internes :**

| Registre | Clé | Valeur |
|---|---|---|
| `_post_connections` | `post_id: int` | `set[WebSocket]` — tous les clients qui consultent la page d'un post |
| `_user_connections` | `user_id: int` | `set[WebSocket]` — toutes les connexions actives d'un utilisateur |

**API publique :**

```python
await manager.connect(websocket, post_id, user_id)      # enregistre la connexion
      manager.disconnect(websocket, post_id, user_id)   # retire la connexion + nettoie les clés vides
await manager.broadcast_to_post(post_id, message)       # diffuse à tous les clients d'un post
await manager.send_to_user(user_id, message)            # notification personnelle (toutes les sessions de l'user)
      manager.connected_to_post(post_id) -> int         # nombre de clients sur un post (health/debug)
      manager.connected_as_user(user_id) -> int         # nombre de connexions d'un user (health/debug)
```

Le manager ne contient **aucune logique métier**. Les échecs d'envoi individuels sont absorbés silencieusement par `_safe_send` (socket déjà fermé) — la déconnexion propre nettoyant le registre par le biais de `disconnect()`.

### Format des messages diffusés

Tous les messages WebSocket partagent le même schéma d'enveloppe :

```json
{
  "type": "comment.created",
  "post_id": 42,
  "payload": { ... }
}
```

Types d'événements définis :

| `type` | Déclenché par |
|---|---|
| `comment.created` | Création d'un commentaire |
| `comment.deleted` | Suppression d'un commentaire |
| `like.created` | Toggle like → ajout |
| `like.deleted` | Toggle like → retrait |

### Variables d'environnement associées

Aucune variable spécifique au manager. Le manager vit en mémoire — pas de persistance, pas de Redis requis (scope single-process).

> **Note multi-process :** En production avec plusieurs workers Uvicorn/Gunicorn, chaque worker a son propre manager en mémoire. Pour partager l'état entre workers, il faudrait un broker externe (Redis Pub/Sub). En single-worker (développement, conteneur unique), le manager fonctionne tel quel.

### Comment tester

Depuis un autre terminal, après démarrage du serveur :

```bash
# Installer wscat si besoin
npm install -g wscat

# Se connecter au canal d'un post (token JWT requis)
wscat -c "ws://localhost:8000/api/ws/posts/1?token=<votre_jwt>"
```

Les messages reçus auront la forme :

```json
{ "type": "comment.created", "post_id": 1, "payload": { "id": 7, "content": "Super article !", "author": { "id": 3, "username": "alice" }, "created_at": "2026-08-07T10:00:00" } }
```

---

## 2. Authentification WebSocket

**Fichier modifié :** `app/middlewares/auth_middleware.py`

### Ce qui a été ajouté

Le middleware a été refactorisé pour partager la logique de décodage JWT entre les routes HTTP et les connexions WebSocket, sans duplication.

**Nouvelles fonctions internes (non exportées) :**

| Fonction | Rôle |
|---|---|
| `_decode_token(token) -> int` | Décode le JWT, extrait et retourne `user_id` (claim `sub`). Lève HTTP 401 si invalide/expiré. |
| `_load_user(user_id, db) -> User` | Charge l'utilisateur via `UserRepository`. Lève HTTP 401 si inexistant. |

Ces deux helpers sont désormais appelés par `get_current_user` (HTTP) **et** `get_current_user_ws` (WebSocket) — la logique de vérification JWT n'est écrite qu'une seule fois.

**Nouvelle dépendance exportée :**

```python
async def get_current_user_ws(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> User | None
```

**Pourquoi un query param `?token=` et non un header `Authorization` ?**
Les headers custom ne sont pas garantis sur tous les clients WebSocket (en particulier React Native sur certaines plateformes). Le query param est le mécanisme portable recommandé pour ce contexte.

**Comportement d'authentification :**

```
Token absent  → websocket.close(code=4401)  →  retourne None
Token invalide → websocket.close(code=4401) →  retourne None
Token valide   → retourne User              →  l'endpoint appelle websocket.accept()
```

Le code `4401` est une convention applicative dans la plage 4000-4999 réservée aux applications par la spec RFC 6455 (équivalent WebSocket du HTTP 401).

### Comment tester

**Connexion sans token (doit échouer) :**

```bash
wscat -c "ws://localhost:8000/api/ws/posts/1"
# Résultat attendu : connexion fermée avec code 4401
```

**Connexion avec token invalide (doit échouer) :**

```bash
wscat -c "ws://localhost:8000/api/ws/posts/1?token=tokenbidon"
# Résultat attendu : connexion fermée avec code 4401
```

**Connexion avec token valide (doit réussir) :**

```bash
# 1. Récupérer un token via login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"motdepasse"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Se connecter avec le token
wscat -c "ws://localhost:8000/api/ws/posts/1?token=$TOKEN"
# Résultat attendu : connexion établie, attente de messages en temps réel
```

### Variables d'environnement associées

Aucune variable nouvelle. Les variables existantes sont utilisées :

| Variable | Usage |
|---|---|
| `SECRET_KEY` | Clé de signature JWT (déjà requise) |
| `ALGORITHM` | Algorithme JWT, défaut `HS256` (déjà requis) |

---

## 3. Endpoint WebSocket

**Fichier :** `app/routes/api/websocket.py`

### Ce qui a été ajouté

```
WS /api/ws/posts/{post_id}?token=<jwt>
```

Canal temps réel en lecture seule pour un post donné. Tout client authentifié qui ouvre cette connexion recevra automatiquement les événements `comment.created`, `comment.deleted`, `like.created` et `like.deleted` émis sur ce post.

**Cycle de vie complet de la connexion :**

```
Client                              Serveur
  │                                    │
  │── WS /api/ws/posts/42?token=xxx ──▶│
  │                                    │ 1. Validation JWT (get_current_user_ws)
  │                                    │    → token absent/invalide : close(4401) ──▶ Client
  │                                    │ 2. PostRepository.get_by_id(42)
  │                                    │    → post introuvable : close(4404) ──────▶ Client
  │                                    │ 3. websocket.accept()
  │◀──────── 101 Switching Protocols ──│
  │                                    │ 4. manager.connect(ws, post_id=42, user_id=3)
  │                                    │
  │◀── {"type":"comment.created",...} ─│  ← diffusé par CommentActions
  │◀── {"type":"like.created",...} ────│  ← diffusé par LikeActions
  │                                    │
  │── (déconnexion client) ───────────▶│
  │                                    │ 5. WebSocketDisconnect
  │                                    │    manager.disconnect(ws, post_id=42, user_id=3)
```

**Codes de fermeture applicatifs :**

| Code | Signification |
|---|---|
| `4401` | Token absent ou invalide (Unauthorized) |
| `4404` | Post introuvable (Not Found) |
| `1000` | Déconnexion normale (client ou serveur) |

**Comportement canal read-only :**
Le serveur maintient la connexion en appelant `receive_text()` en boucle. Les messages envoyés par le client sont ignorés — ce canal est unidirectionnel (serveur → client). Cette approche permet de détecter les déconnexions sans overhead.

### Comment tester

**Scénario complet : ouvrir deux terminaux**

Terminal 1 — Se connecter au canal du post n°1 :

```bash
TOKEN="<votre_jwt>"
wscat -c "ws://localhost:8000/api/ws/posts/1?token=$TOKEN"
# Laisser ce terminal ouvert et en attente
```

Terminal 2 — Créer un commentaire sur le post n°1 :

```bash
curl -X POST http://localhost:8000/api/posts/1/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Commentaire de test temps réel"}'
```

→ Dans le terminal 1, le message suivant doit apparaître immédiatement :

```json
{
  "type": "comment.created",
  "post_id": 1,
  "payload": {
    "id": 7,
    "content": "Commentaire de test temps réel",
    "author": { "id": 3, "username": "alice" },
    "created_at": "2026-08-07T10:00:00"
  }
}
```

**Tester le toggle like :**

```bash
curl -X POST http://localhost:8000/api/posts/1/like \
  -H "Authorization: Bearer $TOKEN"
```

→ Message reçu dans le terminal WebSocket :

```json
{ "type": "like.created", "post_id": 1, "payload": { "liked": true, "likes_count": 5 } }
```

Rappeler la même commande retire le like :

```json
{ "type": "like.deleted", "post_id": 1, "payload": { "liked": false, "likes_count": 4 } }
```

**Tester la fermeture 4404 (post inexistant) :**

```bash
wscat -c "ws://localhost:8000/api/ws/posts/99999?token=$TOKEN"
# Résultat attendu : connexion fermée avec code 4404
```

### Variables d'environnement associées

Aucune variable nouvelle. L'endpoint utilise la DB existante (via `get_db`) et le manager en mémoire.

---

## 4. Branchement des Actions (diffusion temps réel)

**Fichiers modifiés :** `app/actions/comment_actions.py`, `app/actions/like_actions.py`

### Ce qui a été ajouté

Le déclenchement des événements WebSocket est entièrement dans la couche Action — jamais dans les routes. Les routes restent inchangées.

**Principe commun aux deux fichiers :**

```python
import asyncio
from services.websocket_manager import manager

# Après écriture en base + audit confirmés :
asyncio.create_task(manager.broadcast_to_post(post_id, event))
```

`asyncio.create_task()` planifie la diffusion sans bloquer la réponse HTTP : le client REST reçoit sa réponse immédiatement, les clients WebSocket reçoivent l'événement dans la même itération de la boucle d'événements.

---

#### `comment_actions.py` — événements émis

**`create_comment()` → `comment.created`**

Émis après `repo.create()` et `log_action()`, avec les données complètes du commentaire :

```json
{
  "type": "comment.created",
  "post_id": 42,
  "payload": {
    "id": 7,
    "content": "Super article !",
    "author": { "id": 3, "username": "alice" },
    "created_at": "2026-08-07T10:00:00"
  }
}
```

**`delete_comment()` → `comment.deleted`**

Le `post_id` est capturé depuis l'objet `comment` *avant* l'appel `repo.delete()` (l'objet SQLAlchemy est détaché après suppression). L'événement ne transporte que l'identifiant du commentaire supprimé — charge au frontend de retirer l'item de sa liste locale :

```json
{
  "type": "comment.deleted",
  "post_id": 42,
  "payload": { "id": 7 }
}
```

> `update_comment()` n'émet pas d'événement WebSocket — décision produit intentionnelle : l'impact est faible et cela évite la complexité de gestion d'un diff côté client React Native.

---

#### `like_actions.py` — événements émis

**`toggle_like()` → `like.created` ou `like.deleted`**

Le type d'événement est déterminé par le résultat du toggle. Le payload inclut systématiquement le compteur à jour pour que les clients n'aient pas à le recalculer :

```json
{ "type": "like.created", "post_id": 42, "payload": { "liked": true,  "likes_count": 15 } }
{ "type": "like.deleted", "post_id": 42, "payload": { "liked": false, "likes_count": 14 } }
```

---

#### Décision sur `favorite_actions.py`

Les favoris ne sont **pas** diffusés en temps réel — ils restent en polling classique côté frontend. Justification :

- Un favori est une action **privée** (visible uniquement par son auteur dans sa propre liste `GET /api/me/favorites`).
- Il n'y a aucun autre client connecté au même canal qui bénéficierait de recevoir cet événement.
- Le rapport coût/valeur est défavorable : implémenter `send_to_user` pour notifier uniquement l'auteur d'une action qu'il vient lui-même d'initier n'apporte rien d'utile.

### Ordre d'exécution garanti

```
1. Policy check              (lève 403 si non autorisé)
2. repo.create() / delete()  (écriture en base)
3. log_action()              (audit)
4. asyncio.create_task(...)  (diffusion WS — non bloquant)
5. return                    (réponse HTTP au client REST)
```

Les étapes 1-3 sont synchrones et séquentielles. L'étape 4 est planifiée de façon non bloquante : si la diffusion WebSocket échoue (aucun client connecté, socket morte), cela n'affecte jamais la réponse HTTP ni la cohérence de la base de données.

### Variables d'environnement associées

Aucune variable nouvelle. Le branchement est purement en mémoire.

---

## 5. Enregistrement du router

**Fichier modifié :** `main.py`

### Ce qui a été ajouté

Le router WebSocket est importé et enregistré en dernière position dans `main.py` :

```python
from app.routes.api.websocket import router as ws_router
# ...
app.include_router(ws_router)   # WS /api/ws/posts/{post_id}
```

L'ordre dans `main.py` est désormais :

| Router | Préfixe |
|---|---|
| `auth_router` | `/api/auth/...` |
| `posts_router` | `/api/posts/...` |
| `comments_posts_router` | `/api/posts/{id}/comments` |
| `comments_router` | `/api/comments/{id}` |
| `likes_router` | `/api/posts/{id}/like` |
| `favorites_posts_router` | `/api/posts/{id}/favorite` |
| `me_router` | `/api/me/favorites` |
| `ws_router` | `WS /api/ws/posts/{post_id}` |

### Variables d'environnement — récapitulatif complet

Aucune variable nouvelle n'a été introduite par l'ensemble de ce chantier WebSocket. Les variables existantes suffisent :

| Variable | Description | Requis |
|---|---|---|
| `DATABASE_URL` | URL de connexion PostgreSQL | Oui |
| `SECRET_KEY` | Clé de signature JWT | Oui |
| `ALGORITHM` | Algorithme JWT (défaut : `HS256`) | Non |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token (défaut : `60`) | Non |

### Démarrage du serveur

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le canal WebSocket est immédiatement disponible après démarrage. Aucune migration Alembic n'est nécessaire — le WebSocket ne crée aucune table.

---

## Récapitulatif des fichiers créés / modifiés

| Fichier | Statut | Description |
|---|---|---|
| `services/websocket_manager.py` | **Créé** | Gestionnaire singleton des connexions WS |
| `app/middlewares/auth_middleware.py` | **Modifié** | Ajout `_decode_token`, `_load_user`, `get_current_user_ws` |
| `app/routes/api/websocket.py` | **Créé** | Endpoint `WS /api/ws/posts/{post_id}` |
| `app/actions/comment_actions.py` | **Modifié** | Diffusion `comment.created` / `comment.deleted` |
| `app/actions/like_actions.py` | **Modifié** | Diffusion `like.created` / `like.deleted` |
| `main.py` | **Modifié** | Enregistrement de `ws_router` |
