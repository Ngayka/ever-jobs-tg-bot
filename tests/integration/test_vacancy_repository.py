import pytest

from app.database.models import VacancyStatus


def make_job(**overrides):
    job = {
        "id": "dou-123",
        "site": "DOU",
        "title": "Python Developer",
        "companyName": "ACME",
        "jobUrl": "https://example.test/jobs/123",
        "location": {"city": "Kyiv", "country": "Ukraine"},
        "isRemote": True,
        "datePosted": "2026-08-04",
    }
    job.update(overrides)
    return job


@pytest.mark.asyncio
async def test_create_or_get_creates_new_vacancy(vacancy_repository):
    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )

    assert vacancy.id is not None
    assert vacancy.status == VacancyStatus.NEW


@pytest.mark.asyncio
async def test_create_or_get_does_not_duplicate_for_same_user_and_identity(
    vacancy_repository,
):
    first = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )
    second = await vacancy_repository.create_or_get(
        telegram_user_id=1001,
        job=make_job(title="Updated title", jobUrl="https://changed.test"),
    )

    assert second.id == first.id
    assert second.title == first.title


@pytest.mark.asyncio
async def test_same_vacancy_is_separate_for_another_user(vacancy_repository):
    first = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )
    second = await vacancy_repository.create_or_get(
        telegram_user_id=2002, job=make_job()
    )

    assert second.id != first.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "timestamp_field"),
    [
        (VacancyStatus.APPLIED, "applied_at"),
        (VacancyStatus.INTERVIEW, "interview_at"),
        (VacancyStatus.REJECTED, "rejected_at"),
    ],
)
async def test_set_status_sets_status_and_timestamp(
    vacancy_repository, status, timestamp_field
):
    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )

    updated = await vacancy_repository.set_status(
        vacancy_id=vacancy.id,
        telegram_user_id=1001,
        status=status,
    )

    assert updated is not None
    assert updated.status == status
    assert getattr(updated, timestamp_field) is not None


@pytest.mark.asyncio
async def test_user_cannot_change_another_users_vacancy(vacancy_repository):
    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )

    result = await vacancy_repository.set_status(
        vacancy_id=vacancy.id,
        telegram_user_id=2002,
        status=VacancyStatus.APPLIED,
    )
    unchanged = await vacancy_repository.get_by_external_id(
        telegram_user_id=1001,
        site="DOU",
        external_job_id="dou-123",
    )

    assert result is None
    assert unchanged is not None
    assert unchanged.status == VacancyStatus.NEW
    assert unchanged.applied_at is None


@pytest.mark.asyncio
async def test_get_by_external_id_is_scoped_to_user(vacancy_repository):
    vacancy = await vacancy_repository.create_or_get(
        telegram_user_id=1001, job=make_job()
    )

    found = await vacancy_repository.get_by_external_id(
        telegram_user_id=1001,
        site="DOU",
        external_job_id="dou-123",
    )
    not_found = await vacancy_repository.get_by_external_id(
        telegram_user_id=2002,
        site="DOU",
        external_job_id="dou-123",
    )

    assert found is not None
    assert found.id == vacancy.id
    assert not_found is None
