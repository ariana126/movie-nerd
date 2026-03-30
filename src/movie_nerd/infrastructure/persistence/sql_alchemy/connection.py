from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker, Session


class Connection:
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.url = f'postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'
        self.engine = create_engine(self.url)
        self.session = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.session()
