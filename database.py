# database.py file contains SQLAlchemy database

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from fastapi import Depends
from config import settings

# SQLite database url
DATABASE_URL = settings.database_url

# Engine for db
engine = create_async_engine(DATABASE_URL)

# Session for engine
new_session = async_sessionmaker(engine, expire_on_commit=False)

# Parent class for other chart/sheet/etc. classes
Base = DeclarativeBase()

# Dependency function to get database session
async def get_db():
    async with new_session() as session:
        yield session

# Database session ddependency, provides 
# database session and closes it after
SessionDep = Annotated[AsyncSession, Depends(get_db)]

# Service function to create all databases at app start
async def init_db():
    from models import analysis # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
