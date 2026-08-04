from app.job_sources import (
    SOURCE_CATALOG,
    Region,
    SourceType,
    get_sources,
)


def test_default_sources_are_enabled_and_recommended():
    sources = get_sources(Region.WORLDWIDE, {SourceType.JOB_BOARD})

    assert sources
    assert all(SOURCE_CATALOG[source]["enabled"] for source in sources)
    assert all(
        SOURCE_CATALOG[source]["recommended_for_mvp"] for source in sources
    )


def test_sources_are_sorted_by_descending_priority():
    sources = get_sources(Region.WORLDWIDE, {SourceType.JOB_BOARD})
    priorities = [SOURCE_CATALOG[source]["priority"] for source in sources]

    assert priorities == sorted(priorities, reverse=True)


def test_ukraine_job_boards_match_mvp_catalog():
    assert get_sources(Region.UKRAINE, {SourceType.JOB_BOARD}) == [
        "DJINNI",
        "DOU",
        "WORKUA",
        "HAPPYMONDAY",
    ]


def test_generic_adapters_are_not_returned():
    assert get_sources(
        Region.OTHER,
        {SourceType.GENERIC_ADAPTER},
        include_non_recommended=True,
    ) == []


def test_non_recommended_option_adds_enabled_sources():
    recommended = get_sources(Region.EUROPE, {SourceType.JOB_BOARD})
    all_enabled = get_sources(
        Region.EUROPE,
        {SourceType.JOB_BOARD},
        include_non_recommended=True,
    )

    assert set(recommended) < set(all_enabled)
    assert all(SOURCE_CATALOG[source]["enabled"] for source in all_enabled)


def test_recommended_catalog_entries_are_enabled():
    assert not [
        source
        for source, metadata in SOURCE_CATALOG.items()
        if metadata["recommended_for_mvp"] and not metadata["enabled"]
    ]


def test_catalog_priorities_are_valid():
    assert {
        metadata["priority"] for metadata in SOURCE_CATALOG.values()
    } <= {0, 50, 75, 100}
