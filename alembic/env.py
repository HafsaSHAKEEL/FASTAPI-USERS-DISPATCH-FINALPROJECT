from __future__ import with_statement
import logging
from alembic import context
from sqlalchemy import engine_from_config, pool

from database import Base

# Update this import statement to match your project structure

# Configure logging
logger = logging.getLogger('alembic.runtime.migration')

# Retrieve the SQLAlchemy URL from the Alembic configuration
config = context.config

# Set up the target metadata
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    raise Exception("Offline mode is not supported")
else:
    run_migrations_online()
