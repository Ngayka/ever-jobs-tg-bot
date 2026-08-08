from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class VacancyStatus(StrEnum):
    NEW = "new"
    REJECTED = "rejected"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"


class TrackedVacancy(Base):
    __tablename__ = "tracked_vacancies"

    __table_args__ = (
        UniqueConstraint(
            "telegram_user_id",
            "site",
            "external_job_id",
            name="uq_user_site_external_job",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Кому належить ця вакансія.
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    # ID вакансії з ever-jobs:
    # workua-8367057, dou-245042 тощо.
    external_job_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    site: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    company_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    job_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_remote: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    date_posted: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[VacancyStatus] = mapped_column(
        Enum(
            VacancyStatus,
            native_enum=False,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        default=VacancyStatus.NEW,
        nullable=False,
        index=True,
    )

    # Коли вакансія вперше потрапила до бота.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    # Коли користувач востаннє бачив вакансію.
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    interview_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    offer_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


class JobSubscription(Base):
    __tablename__ = "job_subscriptions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    telegram_user_id: Mapped[int] = mapped_column(
        index=True,
    )

    search_term: Mapped[str]

    source_group: Mapped[str]

    enabled: Mapped[bool] = mapped_column(
        default=True,
    )