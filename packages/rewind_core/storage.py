"""SQLite storage bootstrap. No session/event schema before its phase."""

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MIGRATION_REVISION = "0004_ledger"


class Base(DeclarativeBase):
    pass


class AppMetadata(Base):
    __tablename__ = "app_metadata"

    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]


def data_directory() -> Path:
    return Path(os.environ.get("REWIND_DATA_DIR", "data")).resolve()


def make_engine(directory: Path) -> Engine:
    directory.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        URL.create("sqlite", database=str(directory / "rewind.sqlite3")),
        connect_args={"check_same_thread": False, "timeout": 5},
        pool_size=2,
        max_overflow=0,
    )

    @event.listens_for(engine, "connect")
    def configure_sqlite(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    return engine
