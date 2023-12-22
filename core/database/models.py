from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData

from core.database.database import metadata

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tg_id", Integer, nullable=False),
    # Column("email", String, nullable=False),
    Column("username", String),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
)
