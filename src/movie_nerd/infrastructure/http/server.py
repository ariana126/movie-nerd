import os

from pydm import ServiceContainer

from movie_nerd.application.auth.auth_service import AuthService
from movie_nerd.infrastructure.auth import HmacTokenService, Pbkdf2PasswordHasher, SQLAlchemyUserStore
from movie_nerd.infrastructure.http.app_factory import create_app
from movie_nerd.infrastructure.bootstrap.app import App
from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection

App.boot()
service_container = ServiceContainer.get_instance()

connection: Connection = service_container.get_service(Connection)
user_store = SQLAlchemyUserStore(connection=connection)
password_hasher = Pbkdf2PasswordHasher()
token_service = HmacTokenService(secret=os.getenv("AUTH_SECRET", "dev-secret"))

auth_service = AuthService(
    user_store=user_store,
    password_hasher=password_hasher,
    token_service=token_service,
)

app = create_app(auth_service=auth_service)
