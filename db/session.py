from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import settings

# create async db engine
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

# create session for the interacting with db
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> Generator:
    """Get async session"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
