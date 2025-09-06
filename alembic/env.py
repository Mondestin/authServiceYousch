"""
Alembic environment configuration for AuthGhost API
Handles database migrations and schema management
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

# Import your models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.organization import Organization
from app.models.service import Service
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.subscription_tier import SubscriptionTier
from app.models.organization_subscription import OrganizationSubscription
from app.models.revoked_token import RevokedToken
from app.core.database import Base
from app.core.config import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Get database URL from settings"""
    settings = get_settings()
    # Ensure PyMySQL driver is used for MySQL URLs
    url = settings.database_url
    if url.startswith("mysql://") and "pymysql" not in url:
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate it with the Alembic Context.

    """
    # Get database URL from settings
    url = get_url()
    
    # Create engine from config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=url,  # Override URL from settings
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 