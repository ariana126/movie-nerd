"""
Import all ORM-mapped entities so they register on `Base.metadata`.

Anything that subclasses `Base` should be imported here.
"""

from movie_nerd.domain.user import User  # noqa: F401
from movie_nerd.domain.chat import Chat, ChatMessage  # noqa: F401

