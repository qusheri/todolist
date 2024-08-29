from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import db_url
from models import Base

# Создаем асинхронный движок SQLAlchemy
engine = create_async_engine(db_url, echo=True)

# Создаем асинхронную сессию
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Получение сессии для работы с базой данных
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
