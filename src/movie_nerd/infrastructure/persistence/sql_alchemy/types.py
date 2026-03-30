from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.type_api import TypeDecorator
from ddd import Identity


class IdentityType(TypeDecorator):
    impl = String

    cache_ok = True

    def process_bind_param(self, value: Identity, dialect):
        return value.as_string

    def process_result_value(self, value: str, dialect):
        return Identity.from_string(value)