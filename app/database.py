# app/database.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create the database engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Create a session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for routes to access the database
async def get_db():
    async with async_session() as session:
        yield session
