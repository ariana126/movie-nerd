from sqlalchemy import MetaData, Table, Column, String

from .types import IdentityType

metadata = MetaData()

users_table = Table(
    "user",
    metadata,
    Column("id", IdentityType, primary_key=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
)
