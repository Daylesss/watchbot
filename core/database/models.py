from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
from core.database.database import metadata


watch = Table(
    "watch",
    metadata,
    Column("watch_id", Integer, primary_key=True),
    Column("channel_message_id", Integer),
    Column("admin_message_id", Integer, nullable=False),
    Column("price", Integer, nullable=False),
    Column("watch_name", String),
    Column("order_id", Integer),
    Column("status", String, nullable=False, default="for_sale"),
    Column("watch_registred_at", TIMESTAMP, default=datetime.utcnow)
)

user = Table(
    "user",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("tg_id", Integer, nullable=False, unique=True),
    Column("username", String),
    # Column("current_watch_id", Integer),
    Column("order_id", Integer),
    # Column("email", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow)
)

order = Table(
    "order",
    metadata,
    Column("order_id", Integer, primary_key=True),
    Column("tg_id", Integer, ForeignKey("user.tg_id"), nullable=False),
    Column("watch_id", Integer, ForeignKey("watch.watch_id"), nullable=False),
    # Column("user_message_id", Integer),
    Column("book_or_buy", String),
    Column("order_price", Integer),
    Column("network", String),
    Column("address", String),
    Column("order_status", String, default="waiting"),
    Column("order_registred_at", TIMESTAMP, default=datetime.utcnow),
    )
