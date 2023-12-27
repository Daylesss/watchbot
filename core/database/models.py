from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, MetaData
# from sqlalchemy.orm import Mapped, mapped_column
# from core.database.database import Base

# class UsersORM(Base):
#     __table_
#     id: Mapped[int] = mapped_column(primary_key=True)
#     tg_id: Mapped[int] = mapped_column(unique=True)
#     username: Mapped[str]
#     registred_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)



from core.database.database import metadata

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tg_id", Integer, nullable=False),
    Column("booking", JSON),
    # Column("email", String, nullable=False),
    Column("username", String),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
)
