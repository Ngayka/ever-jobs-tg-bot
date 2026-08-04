from enum import StrEnum


class Region(StrEnum):
    UKRAINE = "ukraine"
    EUROPE = "europe"
    NORTH_AMERICA = "north_america"
    ASIA = "asia"
    WORLDWIDE = "worldwide"


class SourceType(StrEnum):
    JOB_BOARDS = "job_boards"
    COMPANIES = "companies"
    ALL = "all"


# Додаємо тільки перевірені джерела,
# які реально існують у Site enum ever-jobs.
JOB_BOARD_SOURCES: dict[Region, list[str]] = {
    Region.UKRAINE: [
        "DOU",
        "DJINNI",
        "HAPPYMONDAY",
        "WORKUA",
    ],
    Region.EUROPE: [],
    Region.NORTH_AMERICA: [],
    Region.ASIA: [],
    Region.WORLDWIDE: [],
}


COMPANY_SOURCES: dict[Region, list[str]] = {
    Region.UKRAINE: [],
    Region.EUROPE: [],
    Region.NORTH_AMERICA: [],
    Region.ASIA: [],
    Region.WORLDWIDE: [],
}


def get_sources(
    region: Region,
    source_type: SourceType,
) -> list[str]:
    job_boards = JOB_BOARD_SOURCES.get(region, [])
    companies = COMPANY_SOURCES.get(region, [])

    if source_type == SourceType.JOB_BOARDS:
        return job_boards.copy()

    if source_type == SourceType.COMPANIES:
        return companies.copy()

    # ALL означає всі рекомендовані й перевірені
    # джерела цього регіону, а не весь ever-jobs.
    return list(
        dict.fromkeys(job_boards + companies)
    )