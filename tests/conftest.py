from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.base import Base
from app.database.repository import VacancyRepository


@pytest_asyncio.fixture
async def vacancy_repository(
    tmp_path,
    monkeypatch,
) -> AsyncIterator[VacancyRepository]:
    database_path = tmp_path / "test_vacancies.db"
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path.as_posix()}"
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    monkeypatch.setattr(
        "app.database.repository.async_session_factory",
        session_factory,
    )

    yield VacancyRepository()

    await engine.dispose()
