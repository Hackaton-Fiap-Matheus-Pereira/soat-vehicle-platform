from alembic import context
from sqlalchemy import engine_from_config, pool

service = context.get_x_argument(as_dictionary=True).get("service", "vehicle_service")
if service == "auth_service":
    from auth_service.config import get_settings
    from auth_service.models import Base
else:
    from vehicle_service.config import get_settings
    from vehicle_service.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("+aiomysql", "+pymysql"))
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()

