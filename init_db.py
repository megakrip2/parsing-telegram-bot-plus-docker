import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sys
print("ВЕРСИЯ ПИТОНА:", sys.version)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:root@localhost:5432/bot_database")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    discount_percentage: Mapped[float] = mapped_column()

async def setup_database():
    async with engine.begin() as conn:
        print("🔨 Начинаем создание таблиц...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблица 'products' успешно создана в PostgreSQL!")

async def main():
    await setup_database()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())

