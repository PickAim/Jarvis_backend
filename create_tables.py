from database.db_config import Base, engine
from database import tables


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_tables()
