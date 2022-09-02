import asyncio
import time

from domain.data_providers.wildberries_data_provider import WildBerriesDataProvider
from database.db_config import SessionLocal
from domain.db_fillers.db_filler import DbFiller
from domain.db_fillers.async_db_filler import AsyncDbFiller
from create_tables import create_tables
from domain.data_providers.async_wildberries_data_provider import AsyncWildberriesDataProvider


def fill_db():
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'
    wildberries_api = WildBerriesDataProvider(key)
    filler = DbFiller(wildberries_api, SessionLocal)
    create_tables()
    filler.fill_categories()
    filler.fill_niches()
    filler.fill_niche_products('Автобаферы')
    filler.fill_niche_price_history('Автобаферы')


async def fill_db_async():
    key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'
    async with AsyncWildberriesDataProvider(key) as api:
        create_tables()
        filler = AsyncDbFiller(api, SessionLocal)
        await filler.fill_categories()
        await filler.fill_niches()
        await filler.fill_niche_products('Автобаферы')
        await filler.fill_niche_price_history('Автобаферы')


if __name__ == '__main__':
    # fixes Windows event loop probem
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start = time.time()
    asyncio.run(fill_db_async())
    print("Time: " + str(time.time() - start))
