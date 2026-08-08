from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database.models import (
    TrackedVacancy,
    VacancyStatus,
)
from app.database.session import async_session_factory


class VacancyRepository:
    async def get_by_id(
        self,
        vacancy_id: int,
        telegram_user_id: int,
    ) -> TrackedVacancy | None:
        async with async_session_factory() as session:
            statement = select(TrackedVacancy).where(
                TrackedVacancy.id == vacancy_id,
                TrackedVacancy.telegram_user_id == telegram_user_id,
            )

            result = await session.execute(statement)

            return result.scalar_one_or_none()

    async def get_by_external_id(
        self,
        *,
        telegram_user_id: int,
        site: str,
        external_job_id: str,
    ) -> TrackedVacancy | None:
        async with async_session_factory() as session:
            statement = select(TrackedVacancy).where(
                TrackedVacancy.telegram_user_id == telegram_user_id,
                TrackedVacancy.site == site,
                TrackedVacancy.external_job_id == external_job_id,
            )

            result = await session.execute(statement)

            return result.scalar_one_or_none()

    async def create_or_get(
        self,
        *,
        telegram_user_id: int,
        job: dict[str, Any],
    ) -> TrackedVacancy:
        site = str(job.get("site") or "unknown")
        external_job_id = str(
            job.get("id")
            or job.get("jobUrl")
            or ""
        )

        existing = await self.get_by_external_id(
            telegram_user_id=telegram_user_id,
            site=site,
            external_job_id=external_job_id,
        )

        if existing:
            return existing

        location_data = job.get("location") or {}
        location = self._build_location(location_data)

        vacancy = TrackedVacancy(
            telegram_user_id=telegram_user_id,
            external_job_id=external_job_id,
            site=site,
            title=str(job.get("title") or "Без назви"),
            company_name=job.get("companyName"),
            job_url=str(job.get("jobUrl") or ""),
            location=location,
            is_remote=bool(job.get("isRemote")),
            date_posted=job.get("datePosted"),
            status=VacancyStatus.NEW,
        )

        async with async_session_factory() as session:
            session.add(vacancy)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

                existing = await self.get_by_external_id(
                    telegram_user_id=telegram_user_id,
                    site=site,
                    external_job_id=external_job_id,
                )

                if existing:
                    return existing

                raise

            await session.refresh(vacancy)

            return vacancy

    async def set_status(
        self,
        *,
        vacancy_id: int,
        telegram_user_id: int,
        status: VacancyStatus,
    ) -> TrackedVacancy | None:
        async with async_session_factory() as session:
            vacancy = await session.get(
                TrackedVacancy,
                vacancy_id,
            )

            if (
                vacancy is None
                or vacancy.telegram_user_id != telegram_user_id
            ):
                return None

            now = datetime.now()

            vacancy.status = status

            if status == VacancyStatus.REJECTED:
                vacancy.rejected_at = now

            elif status == VacancyStatus.APPLIED:
                vacancy.applied_at = now

            elif status == VacancyStatus.INTERVIEW:
                vacancy.interview_at = now

            elif status == VacancyStatus.OFFER:
                vacancy.offer_at = now

            await session.commit()
            await session.refresh(vacancy)

            return vacancy

    @staticmethod
    def _build_location(location: dict[str, Any]) -> str | None:
        parts = [
            location.get("city"),
            location.get("state"),
            location.get("country"),
        ]

        cleaned = [
            str(part).strip()
            for part in parts
            if part
        ]

        return ", ".join(cleaned) or None

    async def get_by_status(
            self,
            *,
            telegram_user_id: int,
            status: VacancyStatus,
    ) -> list[TrackedVacancy]:
        async with async_session_factory() as session:
            statement = (
                select(TrackedVacancy)
                .where(
                    TrackedVacancy.telegram_user_id
                    == telegram_user_id,
                    TrackedVacancy.status == status,
                )
                .order_by(
                    TrackedVacancy.created_at.desc()
                )
            )

            result = await session.execute(statement)

            return list(result.scalars().all())


vacancy_repository = VacancyRepository()