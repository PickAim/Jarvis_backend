from domain.wildberies_data_provider import WildBerriesDataProvider
from database.db_config import SessionLocal
from database.tables import Category, Niche
from sqlalchemy.orm import sessionmaker
from create_tables import create_tables


class DbFiller():

    def __init__(self, api: WildBerriesDataProvider, sessionmaker: sessionmaker):
        self.__api = api
        self.__sessionmaker = sessionmaker

    def fill_categories(self):
        categories = self.__api.get_categories()
        with self.__sessionmaker() as session:
            with session.begin():
                db_categories = []
                for category in categories:
                    db_categories.append(Category(name=category))
                session.add_all(db_categories)

    def fill_niches(self):
        with self.__sessionmaker() as session:
            with session.begin():
                category_to_id = {
                    c.name: c.id for c in session.query(Category).all()
                }
                category_to_niches = self.__api.get_niches(
                    category_to_id.keys()
                )
                db_niches = []
                for category, niches in category_to_niches.items():
                    category_id = category_to_id[category]
                    for niche in niches:
                        db_niches.append(
                            Niche(name=niche,
                                  category_id=category_id)
                        )
                session.add_all(db_niches)


if __name__ == '__main__':
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'
    wildberies_api = WildBerriesDataProvider(key)
    filler = DbFiller(wildberies_api, SessionLocal)
    create_tables()
    filler.fill_categories()
    filler.fill_niches()
