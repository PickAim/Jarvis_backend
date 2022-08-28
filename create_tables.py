from database.db_config import Base, engine
from database import tables


if __name__ == '__main__':
    Base.metadata.create_all(engine)
