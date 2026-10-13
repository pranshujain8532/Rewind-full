from alembic import context
from rewind_core.storage import Base, data_directory, make_engine

target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(url="sqlite://", target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = make_engine(data_directory())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
