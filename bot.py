import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("⚠️ Ошибка: Токен не найден в файле .env!")
print(f"ТОКЕН ИЗ ФАЙЛА: [{TOKEN}]") 

bot = Bot(token=TOKEN)
dp = Dispatcher()
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


@dp.message(Command("top_sales"))
async def cmd_top_sales(message: types.Message):
    async with async_session() as session:
        query = select(Product).order_by(Product.discount_percentage.desc()).limit(3)
        result = await session.execute(query)
        products = result.scalars().all()

        if not products:
            await message.answer("⚠️ База данных пока пуста.")
            return

        response_text = "🔥 **ТОП-3 СКИДКИ ИЗ STEAM** 🔥\n\n"
        for i, product in enumerate(products, 1):
            response_text += f"{i}. 📦 **{product.title}**\n"
            response_text += f"   🛑 Скидка: {product.discount_percentage}%\n"
            response_text += f"   🆔 ID товара: {product.id}\n\n"

        await message.answer(response_text, parse_mode="Markdown")

async def main():
    print("Бот запущен и следит за PostgreSQL! 🟢")
    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())