import re
from typing import Any


ROLE_KEYWORDS: dict[str, set[str]] = {
    "python": {
        "python",
        "django",
        "fastapi",
        "flask",
        "backend",
        "back-end",
        "software engineer",
        "software developer",
        "api developer",
        "odoo",
    },
    "odoo": {
        "odoo",
        "python",
        "erp",
        "odoo developer",
        "odoo engineer",
        "odoo consultant",
    },
    "data": {
        "data analyst",
        "data scientist",
        "data engineer",
        "analytics",
        "sql",
        "pandas",
        "tableau",
        "power bi",
    },
}


EXCLUDED_KEYWORDS = {
    "sales assistant",
    "sales manager",
    "shop assistant",
    "store manager",
    "retail",
    "cashier",
    "продавець",
    "продавец",
    "менеджер з продажу",
    "менеджер по продажам",
    "консультант магазину",
    "оператор call-центру",
    "call center",
}


def normalize_text(value: object) -> str:
    if value is None:
        return ""

    text = str(value).lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_search_keywords(search_term: str) -> set[str]:
    normalized_term = normalize_text(search_term)

    keywords = {
        word
        for word in re.findall(
            r"[a-zа-яіїєґ0-9+#.-]+",
            normalized_term,
        )
        if len(word) >= 3
    }

    for category, related_keywords in ROLE_KEYWORDS.items():
        if category in normalized_term:
            keywords.update(related_keywords)

    return keywords


def calculate_relevance_score(
    job: dict[str, Any],
    search_term: str,
) -> int:
    title = normalize_text(job.get("title"))
    description = normalize_text(job.get("description"))
    company = normalize_text(job.get("companyName"))

    combined_text = " ".join(
        [
            title,
            description,
            company,
        ]
    )

    search_keywords = extract_search_keywords(search_term)

    score = 0

    normalized_search_term = normalize_text(search_term)

    # Повний запит у назві — найсильніший сигнал.
    if normalized_search_term in title:
        score += 10

    for keyword in search_keywords:
        if keyword in title:
            score += 4

        if keyword in description:
            score += 1

    for excluded_keyword in EXCLUDED_KEYWORDS:
        if excluded_keyword in title:
            score -= 10
        elif excluded_keyword in combined_text:
            score -= 4

    return score


def is_job_relevant(
    job: dict[str, Any],
    search_term: str,
    *,
    minimum_score: int = 4,
) -> bool:
    return (
        calculate_relevance_score(
            job=job,
            search_term=search_term,
        )
        >= minimum_score
    )