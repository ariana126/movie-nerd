from pydm import ServiceContainer, EnvParametersBag
from dotenv import load_dotenv

from movie_nerd.domain.service import UserRepository, ChatRepository
from movie_nerd.infrastructure.persistence.sql_alchemy.connection import Connection
from movie_nerd.infrastructure.persistence.sql_alchemy.repositories.chat_repository import SQLAlchemyChatRepository
from movie_nerd.infrastructure.persistence.sql_alchemy.repositories.user_repository import SQLAlchemyUserRepository


class App:
    @staticmethod
    def boot() -> None:
        service_container: ServiceContainer = ServiceContainer.get_instance()

        load_dotenv()
        service_container.set_parameters(EnvParametersBag())

        service_container.bind_parameters(Connection, {
            'host': 'DB_HOST',
            'port': 'DB_PORT',
            'database': 'DB_DATABASE',
            'username': 'DB_USERNAME',
            'password': 'DB_PASSWORD',
        })

        service_container.bind(UserRepository, SQLAlchemyUserRepository)
        service_container.bind(ChatRepository, SQLAlchemyChatRepository)