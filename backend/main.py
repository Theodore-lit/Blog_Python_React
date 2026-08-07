from fastapi import FastAPI

from app.config.database import engine, Base  # noqa: F401 — conservé pour compatibilité

# ---------------------------------------------------------------------------
# Import des routers
# ---------------------------------------------------------------------------
from app.routes.api.auth      import router as auth_router
from app.routes.api.posts     import router as posts_router
from app.routes.api.comments  import posts_router as comments_posts_router
from app.routes.api.comments  import comments_router
from app.routes.api.likes     import router as likes_router
from app.routes.api.favorites import posts_router as favorites_posts_router
from app.routes.api.favorites import me_router
from app.routes.api.websocket import router as ws_router

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Blog API",
    description="API backend du blog — FastAPI + SQLAlchemy + PostgreSQL",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Enregistrement des routers
# Ordre : auth → posts → comments (imbriqués et directs) → likes → favorites
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_posts_router)   # GET/POST /api/posts/{id}/comments
app.include_router(comments_router)          # PUT/DELETE /api/comments/{id}
app.include_router(likes_router)             # POST /api/posts/{id}/like  +  GET /api/posts/{id}/likes/count
app.include_router(favorites_posts_router)   # POST /api/posts/{id}/favorite
app.include_router(me_router)                # GET /api/me/favorites
app.include_router(ws_router)                # WS  /api/ws/posts/{post_id}


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {"status": "ok"}
