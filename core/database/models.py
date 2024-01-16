from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData, Double
from core.database.database import metadata


watch = Table(
    "watch",
    metadata,
    Column("watch_id", Integer, primary_key=True),
    Column("channel_message_id", Integer),
    Column("admin_message_id", Integer),
    Column("unique_file_id", String, unique= True),
    Column("msg_txt", String),
    Column("price", Integer, nullable=False),
    Column("booking_price", Integer, nullable=False),
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
    Column("is_admin", Boolean, nullable=False, default=False),
    Column("order_id", Integer),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow)
)

order = Table(
    "order",
    metadata,
    Column("order_id", Integer, primary_key=True),
    Column("tg_id", Integer, ForeignKey("user.tg_id"), nullable=False),
    Column("watch_id", Integer, ForeignKey("watch.watch_id"), nullable=False),
    Column("book_or_buy", String),
    Column("order_price", Double),
    Column("network", String),
    Column("address", String),
    Column("order_status", String, default="waiting"),
    Column("order_registred_at", TIMESTAMP, default=datetime.utcnow),
    )

transaction = Table(
    "transaction",
    metadata,
    Column("transaction_id", Integer, primary_key=True),
    Column("tg_id", Integer, nullable=False),
    Column("watch_id", Integer, ForeignKey("watch.watch_id"), nullable=False),
    Column("transaction_data", JSON, nullable=False),
    Column("transaction_time", TIMESTAMP, default=datetime.utcnow)
)

watch_file = Table(
    "watch_file",
    metadata,
    Column("watch_file_id", Integer, primary_key=True),
    Column("unique_file_id", String, nullable=False),
    Column("file_id", String, nullable=False),
    Column("file_type", String, nullable=False),
    Column("watch_file_registred_at", TIMESTAMP, default=datetime.utcnow)
)