import asyncio
import aiohttp
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import delete

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:root@localhost:5432/bot_database")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    discount_percentage: Mapped[float] = mapped_column()

async def fetch_steam_discounts():
    print("🌐 Подключаемся к серверу скидок Steam...")
    url = "https://www.cheapshark.com/api/1.0/deals?storeID=1&sortBy=Savings&pageSize=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                print("✅ Данные успешно скачаны!")
                return await response.json()
            else:
                print(f"❌ Ошибка сети: {response.status}")
                return []

async def update_database(games_data):
    async with async_session() as session:
        print("🧹 Очищаем таблицу от старых данных...")
        await session.execute(delete(Product))     
        new_products = []
        for game in games_data:
            title = game.get("title", "Неизвестная игра")
            discount = round(float(game.get("savings", 0.0)), 1)
            new_products.append(Product(title=title, discount_percentage=discount))
            print(f"🎮 Найдена скидка: {title} - {discount}%")
        session.add_all(new_products)
        await session.commit()
        print("💾 Новые товары успешно сохранены в БД!")

async def main():
    games = await fetch_steam_discounts()
    if games:
        await update_database(games)
    await engine.dispose()
if __name__ == "__main__":
    asyncio.run(main())