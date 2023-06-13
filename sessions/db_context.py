from jarvis_db.db_config import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DbContext:
    def __init__(self, connection_sting: str = 'sqlite://', echo=False) -> None:
        if echo:
            import logging
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        engine = create_engine(connection_sting)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.session = session
