from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Injection de l'URL depuis les settings applicatifs (évite la duplication
# dans alembic.ini et garantit une source unique de vérité pour DATABASE_URL)
# ---------------------------------------------------------------------------
from app.config.settings import settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# ---------------------------------------------------------------------------
# Import de TOUS les modèles pour que autogenerate détecte les tables.
# Ajouter ici tout nouveau modèle créé dans app/models/.
# ---------------------------------------------------------------------------
from app.config.database import Base  # noqa: F401 — Base doit être importée avant les modèles

from app.models.user      import User       # noqa: F401
from app.models.post      import Post       # noqa: F401
from app.models.comment   import Comment    # noqa: F401
from app.models.like      import Like       # noqa: F401
from app.models.favorite  import Favorite   # noqa: F401
from app.models.audit_log import AuditLog   # noqa: F401

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Fonctions de migration standard générées par Alembic (inchangées)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
