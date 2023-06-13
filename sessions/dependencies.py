from fastapi import Depends

from sessions.db_context import DbContext

__DB_CONTEXT = None


def __db_context_depends() -> DbContext:
    global __DB_CONTEXT
    if __DB_CONTEXT is None:
        __DB_CONTEXT = DbContext("sqlite:///test.db", echo=True)
    return __DB_CONTEXT


def session_depend(db_context: DbContext = Depends(__db_context_depends)):
    with db_context.session() as session, session.begin():
        yield session
