from jarvis_db.db_config import Base
from sqlalchemy import Engine, event, create_engine
from sqlalchemy.orm import sessionmaker

from jarvis_backend.sessions.dependencies import init_defaults

__DEFAULTS_INITED = False
__DB_CONTEXT = None


class TestDbContext:
    def __init__(self, connection_sting: str = 'sqlite://', echo=False) -> None:
        if echo:
            import logging

            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        if connection_sting.startswith("sqlite://"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        engine = create_engine(connection_sting)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.session = session


def db_context_depends() -> TestDbContext:
    global __DB_CONTEXT
    if __DB_CONTEXT is None:
        __DB_CONTEXT = TestDbContext("sqlite:///test.db")
    return __DB_CONTEXT


def _get_session(db_context):
    global __DEFAULTS_INITED
    session = db_context.session()
    session.begin()
    if not __DEFAULTS_INITED:
        init_defaults(session)
        __DEFAULTS_INITED = True
    return session
