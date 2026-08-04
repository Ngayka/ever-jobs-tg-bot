import pytest

from app.services.job_relevance import (
    calculate_relevance_score,
    is_job_relevant,
)


@pytest.mark.parametrize(
    "job",
    [
        {"title": "Python Developer", "description": "", "companyName": "ACME"},
        {
            "title": "Backend Developer",
            "description": "We use Python and Django.",
            "companyName": "ACME",
        },
        {
            "title": "Odoo Developer",
            "description": "Requirements include Python.",
            "companyName": "ACME",
        },
    ],
)
def test_relevant_python_jobs_pass(job):
    assert is_job_relevant(job, "python developer")


@pytest.mark.parametrize(
    "job",
    [
        {
            "title": "Продавець-консультант Apple",
            "description": "Продаж техніки в магазині.",
            "companyName": "Apple reseller",
        },
        {"title": "Sales Manager", "description": "B2B sales", "companyName": "ACME"},
        {},
    ],
)
def test_irrelevant_jobs_do_not_pass(job):
    assert not is_job_relevant(job, "python developer")


def test_none_fields_do_not_raise_and_are_irrelevant():
    job = {"title": None, "description": None, "companyName": None}

    assert calculate_relevance_score(job, "python developer") == 0
    assert not is_job_relevant(job, "python developer")


def test_exact_title_match_scores_higher_than_description_only_match():
    title_match = {
        "title": "Python Developer",
        "description": "",
        "companyName": "ACME",
    }
    description_match = {
        "title": "Engineer",
        "description": "Python developer",
        "companyName": "ACME",
    }

    assert calculate_relevance_score(
        title_match, "python developer"
    ) > calculate_relevance_score(description_match, "python developer")
