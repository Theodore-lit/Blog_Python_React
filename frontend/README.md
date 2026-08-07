# Mini Blog — Frontend React + Vite

> React 18 · React Router 6 · Axios · Vite 5

---

## Table des matières

1. [Socle technique](#1-socle-technique)
2. [Authentification](#2-authentification)
3. [Posts](#3-posts)
4. [Commentaires](#4-commentaires)
5. [Likes](#5-likes)
6. [Favoris](#6-favoris)
7. [WebSocket temps réel](#7-websocket-temps-réel)

---

## Prérequis globaux

| Prérequis | Détail |
|---|---|
| Node.js ≥ 18 | Runtime JavaScript |
| Backend FastAPI démarré | `cd backend && uvicorn main:app --reload` |
| Variables d'environnement | Voir `.env.example` à la racine de `frontend/` |

```bash
# Installation des dépendances
cd frontend
npm install

# Démarrage du serveur de développement
npm run dev
# → http://localhost:5173
```

---

## Variables d'environnement

Créer `frontend/.env` (copier `.env.example`) :

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/ws
```

---

## 1. Socle technique

**Fichiers créés :**
- `src/api/axios.js`
- `src/services/token.service.js`
- `src/utils/formatDate.js`

### `token.service.js`

Seul point d'accès à `localStorage` pour le JWT. Aucun composant ni hook
ne lit ou écrit le token directement.

```js
import tokenService from './services/token.service.js'

tokenService.getToken()        // → string | null
tokenService.setToken(token)   // stocke le token
tokenService.clearToken()      // supprime le token
```

### `axios.js`

Instance Axios préconfigurée avec :
- `baseURL` depuis `VITE_API_URL`
- Intercepteur request : ajoute `Authorization: Bearer <token>` si un token existe
- Intercepteur response : sur 401, efface le token et redirige vers `/login`

Tous les fichiers `*.api.js` importent cette instance — jamais `axios` directement.

```js
import api from './api/axios.js'
const { data } = await api.get('/api/posts')
```

### `formatDate.js`

Deux helpers de formatage locale `fr-FR` :

```js
import { formatDate, formatDateTime } from './utils/formatDate.js'

formatDate('2026-08-07T10:00:00')      // → "07 août 2026"
formatDateTime('2026-08-07T10:00:00')  // → "07 août 2026 à 10:00"
```

### Comment tester

Ouvrir la console du navigateur sur `http://localhost:5173` et vérifier :

```js
// Aucune erreur d'import au démarrage de l'app
// Le réseau (onglet Network) ne montre pas de requête sans header Authorization
// quand aucun token n'est stocké
```

---

## 2. Authentification

**Fichiers créés :**
- `src/api/auth.api.js`
- `src/context/AuthContext.jsx`
- `src/hooks/useAuth.js`
- `src/routes/PrivateRoute.jsx`
- `src/routes/PublicRoute.jsx`
- `src/pages/Login.jsx`
- `src/pages/Register.jsx`

### Flux

```
Login.jsx / Register.jsx
  → useAuth()            (hook wrapper du contexte)
    → AuthContext        (login / register / logout / user / isAuthenticated)
      → auth.api.js      (login, register, getMe)
        → axios.js       (POST /api/auth/login, etc.)
```

### `AuthContext`

Exposé via `<AuthProvider>` dans `main.jsx`. Valeurs disponibles :

| Valeur | Type | Description |
|---|---|---|
| `user` | `object \| null` | Utilisateur connecté (`id`, `username`, `email`) |
| `isAuthenticated` | `boolean` | `true` si un user est chargé |
| `isLoading` | `boolean` | `true` pendant la vérification initiale du token |
| `login(email, pass)` | `async fn` | Appelle POST /login, stocke le token, charge `/me` |
| `register(u, e, p)` | `async fn` | Appelle POST /register puis `login()` |
| `logout()` | `fn` | Efface le token, vide `user` |

Au montage, `AuthProvider` rappelle `GET /api/auth/me` si un token est déjà
présent en `localStorage` — cela restaure la session sans demander un nouveau login.

### `PrivateRoute` / `PublicRoute`

- `PrivateRoute` : redirige vers `/login` si non authentifié.
- `PublicRoute` : redirige vers `/` si déjà authentifié (évite d'accéder à `/login` quand on est connecté).
- Les deux attendent la fin de `isLoading` avant de décider.

### Comment tester

1. Démarrer le backend : `uvicorn main:app --reload`
2. Démarrer le frontend : `npm run dev`
3. Aller sur `http://localhost:5173/register` → créer un compte
4. Vérifier la redirection vers `/` après inscription
5. Aller sur `http://localhost:5173/login` → tester un mauvais mot de passe (message d'erreur attendu)
6. Se reconnecter → vérifier que `localStorage` contient `auth_token`
7. Rafraîchir la page → la session doit être restaurée sans redemander le login

### Variables d'environnement

Aucune variable nouvelle — `VITE_API_URL` suffit.

### Endpoint backend requis

| Méthode | URL | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Retourne `{ access_token }` |
| `POST` | `/api/auth/register` | Crée un utilisateur |
| `GET` | `/api/auth/me` | Retourne l'utilisateur courant (JWT requis) |

---

## 3. Posts

**Fichiers créés :**
- `src/api/posts.api.js`
- `src/hooks/useFetchPosts.js`
- `src/hooks/useFetchPost.js`
- `src/components/blog/PostCard.jsx`
- `src/pages/Home.jsx`
- `src/pages/PostDetail.jsx`
- `src/pages/PostForm.jsx`

### Flux

```
Home.jsx          → useFetchPosts  → getPosts(page)  → GET /api/posts
PostDetail.jsx    → useFetchPost   → getPost(id)     → GET /api/posts/{id}
PostForm.jsx      → (direct)       → createPost/updatePost
```

### `posts.api.js`

| Fonction | Endpoint | Auth |
|---|---|---|
| `getPosts(page, limit)` | `GET /api/posts` | Non |
| `getPost(id)` | `GET /api/posts/{id}` | Non |
| `createPost(data)` | `POST /api/posts` | Oui |
| `updatePost(id, data)` | `PUT /api/posts/{id}` | Oui |
| `deletePost(id)` | `DELETE /api/posts/{id}` | Oui |

`getPosts` convertit le numéro de page en `skip` : `skip = (page - 1) * limit`.

### `useFetchPosts`

Gère `posts`, `total`, `page`, `loading`, `error`. Expose `fetchPage(n)` pour
la pagination. Déclenche le premier chargement au montage.

### `useFetchPost`

Annulation des requêtes en vol (flag `cancelled`) pour éviter les mises à jour
d'état sur un composant démonté.

### `PostCard`

Composant purement présentationnel — reçoit `post` en props, ne fait aucun
appel API. Tronque le contenu à 160 caractères.

### `PostDetail`

Monte `CommentList`, `LikeButton`, `FavoriteButton` (implémentés aux étapes
suivantes). Affiche les contrôles Modifier/Supprimer uniquement pour l'auteur.

### `PostForm`

Fonctionne en mode création (`/posts/new`) et édition (`/posts/:id/edit`).
En mode édition, pré-charge le contenu via `getPost(id)` au montage.

### Comment tester

1. `http://localhost:5173/` → liste des posts avec pagination
2. Cliquer sur un titre → page de détail
3. Connecté → bouton `+ Nouveau post` → formulaire de création
4. Créer un post → redirection vers sa page de détail
5. Auteur connecté → liens Modifier / Supprimer visibles

### Endpoints backend requis

| Méthode | URL |
|---|---|
| `GET` | `/api/posts?skip=0&limit=20` |
| `GET` | `/api/posts/{id}` |
| `POST` | `/api/posts` |
| `PUT` | `/api/posts/{id}` |
| `DELETE` | `/api/posts/{id}` |

---

## 4. Commentaires

**Fichiers créés :**
- `src/api/comments.api.js`
- `src/hooks/useComments.js`
- `src/components/blog/CommentItem.jsx`
- `src/components/blog/CommentList.jsx`

**Fichier modifié :**
- `src/pages/PostDetail.jsx` — ajout de `commentSocketRef` (useRef) transmis à `CommentList`

### Flux

```
CommentList.jsx
  → useComments(postId)
    → getComments / createComment / deleteComment
      → GET /api/posts/{id}/comments
      → POST /api/posts/{id}/comments
      → DELETE /api/comments/{id}
```

### `useComments`

| Valeur / Fonction | Description |
|---|---|
| `comments` | Liste courante des commentaires |
| `loading` / `error` | États de chargement |
| `addComment(content)` | Appelle l'API puis ajoute le commentaire à l'état local |
| `removeComment(id)` | Appelle l'API puis retire le commentaire de l'état local |
| `applyRealtimeEvent(event)` | Appelé par `usePostSocket` pour mettre à jour la liste sans rechargement |

### Gestion temps réel (préparation étape 7)

`applyRealtimeEvent` distingue deux cas :
- `comment.created` : insère le commentaire si son `id` n'est pas déjà présent (évite le doublon quand c'est l'utilisateur courant qui vient de poster).
- `comment.deleted` : filtre le commentaire par `id`.

`CommentList` expose cette fonction via `socketRef.current` — une ref transmise
par `PostDetail` et lue par `usePostSocket` à l'étape 7.

### `CommentItem`

Purement présentationnel. Reçoit `comment`, `canDelete` (booléen) et `onDelete`
(callback). La logique de suppression reste dans `useComments`.

### Comment tester

1. Ouvrir la page d'un post → les commentaires existants s'affichent
2. Connecté → formulaire visible en bas de la liste
3. Soumettre un commentaire → il apparaît immédiatement dans la liste
4. Auteur du commentaire → bouton Supprimer visible, cliquer → retrait immédiat
5. Ouvrir deux onglets sur le même post → créer un commentaire dans l'un → il apparaîtra en temps réel dans l'autre après l'étape 7

### Endpoints backend requis

| Méthode | URL |
|---|---|
| `GET` | `/api/posts/{id}/comments` |
| `POST` | `/api/posts/{id}/comments` |
| `DELETE` | `/api/comments/{id}` |

---

## 5. Likes

**Fichiers créés :**
- `src/api/likes.api.js`
- `src/hooks/useLike.js`
- `src/components/blog/LikeButton.jsx`

**Fichier modifié :**
- `src/pages/PostDetail.jsx` — ajout de `likeSocketRef` transmis à `LikeButton`

### Flux

```
LikeButton.jsx
  → useLike(postId)
    → toggleLike / getLikeCount
      → POST /api/posts/{id}/like
      → GET  /api/posts/{id}/likes/count
```

### Mise à jour optimiste + rollback

`useLike` bascule l'état local (`liked`, `count`) **immédiatement** avant l'appel API,
pour une UX sans latence perceptible. Un snapshot de l'état précédent est gardé en `ref`.
Si l'appel API échoue, le snapshot est restauré automatiquement.

```
Clic utilisateur
  → setLiked(!liked) + setCount(±1)   ← immédiat (optimiste)
  → await toggleLike(postId)
      ✓ succès → setLiked/setCount depuis la réponse serveur (source de vérité)
      ✗ erreur → rollback vers snapshot
```

### Synchronisation temps réel (préparation étape 7)

`applyRealtimeEvent` met à jour `count` depuis le payload WebSocket quand un
autre utilisateur like/unlike — sans changer `liked` (qui est propre à l'utilisateur courant).

`LikeButton` expose cette fonction via `socketRef.current`, lue par `usePostSocket`.

### Comment tester

1. Ouvrir la page d'un post connecté
2. Cliquer ♡ → basculement immédiat vers ♥ + compteur +1
3. Re-cliquer → retour ♡ + compteur -1
4. Ouvrir deux onglets : liker dans l'un → après l'étape 7, le compteur se met à jour dans l'autre en temps réel

### Endpoints backend requis

| Méthode | URL | Auth |
|---|---|---|
| `POST` | `/api/posts/{id}/like` | Oui (toggle) |
| `GET` | `/api/posts/{id}/likes/count` | Non |

---

## 6. Favoris

**Fichiers créés :**
- `src/api/favorites.api.js`
- `src/hooks/useFavorite.js`
- `src/components/blog/FavoriteButton.jsx`
- `src/pages/Favorites.jsx`

### Flux

```
FavoriteButton.jsx  → useFavorite(postId) → toggleFavorite → POST /api/posts/{id}/favorite
Favorites.jsx       → (direct api)        → getMyFavorites → GET  /api/me/favorites
```

### `useFavorite`

Même pattern optimiste que `useLike` : bascule immédiate de l'état local,
rollback via `snapshot` ref si l'appel API échoue.

L'état initial est `false` — le backend ne fournit pas d'endpoint
`GET /api/posts/{id}/favorite/me`, donc l'état réel n'est pas connu avant
le premier toggle. Ce choix est intentionnel : la synchronisation fine de
l'état "est-ce que j'ai déjà mis ce post en favori ?" peut être ajoutée
via un endpoint dédié si le besoin émerge.

### `Favorites.jsx`

Page protégée par `PrivateRoute`. Charge la liste paginée des posts favoris
de l'utilisateur connecté. Réutilise `PostCard` pour l'affichage — aucune
duplication de composant.

L'appel API est fait directement dans `useEffect` (sans hook dédié) car
la page est simple et n'a pas besoin de partager son état avec d'autres
composants. Un hook `useFetchFavorites` serait justifié si la logique
devenait plus complexe.

### Décision : pas de WebSocket sur les favoris

Les favoris ne sont pas diffusés en temps réel (voir backend readme, section 4).
Cette page reste en polling : l'utilisateur recharge manuellement ou navigue
vers la page pour voir la liste à jour.

### Comment tester

1. Se connecter et aller sur la page d'un post
2. Cliquer ☆ Favori → basculement immédiat vers ★ Favori (jaune)
3. Re-cliquer → retour ☆
4. Aller sur `http://localhost:5173/favorites` → la liste des posts favoris apparaît
5. Tenter d'accéder à `/favorites` sans être connecté → redirection vers `/login`

### Endpoints backend requis

| Méthode | URL | Auth |
|---|---|---|
| `POST` | `/api/posts/{id}/favorite` | Oui (toggle) |
| `GET` | `/api/me/favorites` | Oui |

---

## 7. WebSocket temps réel

**Fichier créé :**
- `src/hooks/usePostSocket.js`

**Fichier modifié :**
- `src/pages/PostDetail.jsx` — appel de `usePostSocket` avant les returns conditionnels

### Ce qui a été ajouté

`usePostSocket(postId, commentRef, likeRef)` gère le cycle de vie complet
de la connexion WebSocket au canal d'un post :

```
PostDetail monte
  → usePostSocket(postId, commentRef, likeRef)
      → new WebSocket(`${VITE_WS_URL}/posts/${postId}?token=...`)
          ws.onmessage → parse JSON → route vers commentRef.current(event)
                                              ou likeRef.current(event)
PostDetail démonte
  → ws.close(1000)   ← code 1000 = fermeture volontaire, pas de reconnexion
```

### Routage des événements

Les callbacks sont lus depuis les refs au moment du message — pas besoin de
les déclarer comme dépendances de `useEffect` (les refs ne changent jamais
d'identité) :

| `event.type` | Ref appelée | Effet |
|---|---|---|
| `comment.created` | `commentRef.current` | `useComments.applyRealtimeEvent` → insère le commentaire |
| `comment.deleted` | `commentRef.current` | `useComments.applyRealtimeEvent` → retire le commentaire |
| `like.created` | `likeRef.current` | `useLike.applyRealtimeEvent` → met à jour le compteur |
| `like.deleted` | `likeRef.current` | `useLike.applyRealtimeEvent` → met à jour le compteur |

### Reconnexion avec backoff

En cas de fermeture inattendue (coupure réseau, redémarrage serveur), le hook
se reconnecte automatiquement avec un délai croissant :

```
1ère tentative : 2s
2ème tentative : 4s
3ème tentative : 8s
4ème+ tentative : 16s (plafonné)
```

Une fermeture avec le code `1000` (démontage du composant) n'entraîne **pas**
de reconnexion.

### Point technique — règle des hooks

`usePostSocket` est appelé **avant** tous les `return` conditionnels de
`PostDetail`, conformément à la règle des hooks React. Le hook reçoit
`post ? Number(id) : null` — quand `post` n'est pas encore chargé,
`postId` vaut `null` et le hook s'abstient d'ouvrir la socket.

### Variables d'environnement

| Variable | Valeur par défaut |
|---|---|
| `VITE_WS_URL` | `ws://localhost:8000/api/ws` |

### Comment tester

**Test basique :**
1. Ouvrir `http://localhost:5173/posts/1` dans deux onglets (connecté)
2. Dans l'onglet A, créer un commentaire → il apparaît dans l'onglet B sans rechargement
3. Dans l'onglet A, liker → le compteur se met à jour dans l'onglet B

**Test de reconnexion :**
1. Ouvrir la page d'un post
2. Arrêter le serveur backend (`Ctrl+C`)
3. Relancer le backend
4. Vérifier dans la console que la connexion WebSocket se rétablit automatiquement

**Vérifier dans la console navigateur :**
```
# Aucune erreur "Cannot call hooks conditionally"
# Onglet Network → WS → messages reçus en temps réel
```

---

## 8. Composants UI génériques

**Fichiers créés :**
- `src/components/ui/BaseButton.jsx`
- `src/components/ui/BaseInput.jsx`
- `src/components/ui/BaseModal.jsx`

**Fichiers mis à jour :**
- `src/pages/Login.jsx`
- `src/pages/Register.jsx`
- `src/pages/PostForm.jsx`
- `src/components/blog/CommentList.jsx`

### `BaseButton`

```jsx
<BaseButton variant="primary" disabled={busy} type="submit">
  Enregistrer
</BaseButton>
```

| Prop | Type | Défaut | Description |
|---|---|---|---|
| `variant` | `'primary' \| 'danger' \| 'ghost'` | `'primary'` | Couleur du bouton |
| `disabled` | `boolean` | `false` | Désactive + opacité 0.55 |
| `type` | `string` | `'button'` | Attribut HTML type |
| `onClick` | `function` | — | Handler clic |
| `style` | `object` | `{}` | Styles supplémentaires (ex: `width:'100%'`) |

### `BaseInput`

```jsx
<BaseInput id="email" type="email" label="Email" error={errors.email} required />
<BaseInput as="textarea" id="content" label="Contenu" rows={10} />
```

| Prop | Type | Défaut | Description |
|---|---|---|---|
| `as` | `'input' \| 'textarea'` | `'input'` | Élément HTML rendu |
| `label` | `string` | — | Label affiché au-dessus |
| `id` | `string` | — | Lie le label au champ (`htmlFor`) |
| `error` | `string` | — | Message d'erreur (bord rouge + texte) |

Accepte tous les autres attributs HTML natifs via `...props`.

### `BaseModal`

```jsx
<BaseModal isOpen={showModal} onClose={() => setShowModal(false)} title="Confirmation">
  <p>Voulez-vous vraiment supprimer ce post ?</p>
  <BaseButton variant="danger" onClick={handleConfirm}>Supprimer</BaseButton>
</BaseModal>
```

- Fermeture sur touche `Escape` et clic sur l'overlay
- `role="dialog"` + `aria-modal="true"` pour l'accessibilité
- Non utilisée dans les pages actuelles (prête à l'emploi pour les futures confirmations)

### Intégration

Tous les formulaires (`Login`, `Register`, `PostForm`, `CommentList`) utilisent
désormais `BaseInput` et `BaseButton` — plus aucun `<input>` ou `<button>` nu
dans les formulaires.

---

## Récapitulatif — Structure finale

```
frontend/src/
├── api/             axios.js · auth · posts · comments · likes · favorites
├── components/
│   ├── blog/        PostCard · CommentList · CommentItem · LikeButton · FavoriteButton
│   └── ui/          BaseButton · BaseInput · BaseModal
├── context/         AuthContext
├── hooks/           useAuth · useFetchPosts · useFetchPost · useComments
│                    useLike · useFavorite · usePostSocket
├── pages/           Home · Login · Register · PostDetail · PostForm · Favorites
├── routes/          PrivateRoute · PublicRoute
├── services/        token.service
└── utils/           formatDate
```

Pour démarrer :
```bash
cd frontend
npm install
npm run dev      # → http://localhost:5173
```
