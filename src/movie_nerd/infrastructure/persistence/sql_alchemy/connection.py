from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker, Session

from movie_nerd.infrastructure.persistence.sql_alchemy.orm import Base
from movie_nerd.infrastructure.persistence.sql_alchemy import models  # noqa: F401


class Connection:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.url = f'postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
        self.engine = create_engine(self.url)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self) -> Session:
        return self.session()
