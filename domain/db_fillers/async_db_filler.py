import asyncio
from domain.data_providers.async_wildberies_data_provider import AsyncWildberiesDataProvider
from sqlalchemy.orm import sessionmaker
from database.tables import Category, Niche, Product, ProductCostHistory


class AsyncDbFiller:

    def __init__(self, api: AsyncWildberiesDataProvider, sessionmaker: sessionmaker) -> None:
        self.__api = api
        self.__sessionmaker = sessionmaker

    async def fill_categories(self):
        categories = await self.__api.get_categories()
        with self.__sessionmaker() as session:
            with session.begin():
                db_categories = []
                for category in categories:
                    db_categories.append(Category(name=category))
                session.add_all(db_categories)

    async def fill_niches(self):
        with self.__sessionmaker() as session:
            with session.begin():
                category_to_id = {
                    c.name: c.id for c in session.query(Category).all()
                }
                category_to_niches = await self.__api.get_niches(
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

    async def fill_niche_products(self, niche: str, pages: int = 1):
        with self.__sessionmaker() as session:
            with session.begin():
                db_products = []
                niche_id = session.query(Niche).filter(
                    Niche.name == niche
                ).first().id
                products = await self.__api.get_products_by_niche(niche, pages)
                for product in products:
                    db_products.append(Product(
                        id=product[1],
                        name=product[0],
                        niche_id=niche_id
                    ))
                session.add_all(db_products)

    async def fill_niche_price_history(self, niche: str):
        with self.__sessionmaker() as session:
            with session.begin():
                db_histories = []
                niche_id = session.query(Niche).filter(
                    Niche.name == niche).first().id
                products: list[Product] = session.query(
                    Product).filter(Product.niche_id == niche_id).all()
                tasks = []
                for product in products:
                    tasks.append(asyncio.create_task(
                        self.__api.get_product_price_history(product.id)))
                product_histories = await asyncio.gather(*tasks)
                product_id_to_histories = dict(
                    zip((p.id for p in products), product_histories))
                for product_id, histories in product_id_to_histories.items():
                    for history in histories:
                        db_histories.append(ProductCostHistory(
                            cost=history[0],
                            date=history[1],
                            product_id=product_id
                        ))
                session.add_all(db_histories)
