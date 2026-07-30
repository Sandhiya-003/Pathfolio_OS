"""Re-exports the DB client singletons that already live in each submodule.

Must NOT construct new instances here -- each client (SQLite connection,
Chroma collection) is already created once at the bottom of its own module.
"""

from app.db.chroma_db import chroma_client
from app.db.sqlite_db import sqlite_db

__all__ = ["chroma_client", "sqlite_db"]
