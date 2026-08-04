import pytest

from app.handlers.search import format_job_card


def make_job(**overrides):
    job = {
        "title": "Python Developer",
        "companyName": "ACME",
        "jobUrl": "https://example.test/jobs/1",
        "site": "DOU",
        "datePosted": "2026-08-04",
        "isRemote": True,
        "location": {"city": "Kyiv", "country": "Ukraine"},
    }
    job.update(overrides)
    return job


def test_full_vacancy_card():
    card = format_job_card(make_job(), current_index=0, total_jobs=5)

    assert "<b>Vacancy 1 from 5</b>" in card
    assert "<b>Python Developer</b>" in card
    assert "ACME" in card
    assert "Kyiv, Ukraine" in card
    assert "Remote: Yes" in card
    assert 'href="https://example.test/jobs/1"' in card


def test_missing_url_has_no_link():
    card = format_job_card(make_job(jobUrl=None), current_index=0, total_jobs=1)

    assert "href=" not in card
    assert "View Vacancy" not in card


@pytest.mark.parametrize("location", [{}, None])
def test_empty_or_none_location_is_not_specified(location):
    card = format_job_card(
        make_job(location=location), current_index=0, total_jobs=1
    )

    assert "Not specified" in card


def test_user_supplied_html_is_escaped():
    card = format_job_card(
        make_job(
            title="Python <Lead> & Developer",
            companyName="A&B > Labs",
        ),
        current_index=1,
        total_jobs=12,
    )

    assert "Python &lt;Lead&gt; &amp; Developer" in card
    assert "A&amp;B &gt; Labs" in card
    assert "Python <Lead>" not in card
    assert "A&B > Labs" not in card
    assert "<b>Vacancy 2 from 12</b>" in card


def test_url_html_characters_are_escaped_in_attribute():
    card = format_job_card(
        make_job(jobUrl='https://example.test/?a=1&b=<two>"'),
        current_index=0,
        total_jobs=1,
    )

    assert 'href="https://example.test/?a=1&amp;b=&lt;two&gt;&quot;"' in card
