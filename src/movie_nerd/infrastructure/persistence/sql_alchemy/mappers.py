from sqlalchemy.orm import registry

from movie_nerd.domain import User
from .tables import users_table, metadata

mapper_registry = registry(metadata=metadata)

mapper_registry.map_imperatively(User, users_table)