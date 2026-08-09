import pytest

from app.docs.job_sources import (
    SOURCE_CATALOG,
    SourceGroup,
    SourceType,
    get_enabled_sources,
    validate_source_catalog,
)


REQUIRED_FIELDS = {
    "group",
    "source_type",
    "enabled",
    "recommended_for_mvp",
    "priority",
}


def expected_enabled_sources(
    group: SourceGroup | None = None,
    *,
    mvp_only: bool = False,
) -> list[str]:
    matching_sources = [
        source
        for source, metadata in SOURCE_CATALOG.items()
        if metadata["enabled"]
        and (group is None or metadata["group"] == group)
        and (not mvp_only or metadata["recommended_for_mvp"])
    ]
    return sorted(
        matching_sources,
        key=lambda source: (-SOURCE_CATALOG[source]["priority"], source),
    )


def test_real_source_catalog_is_valid():
    validate_source_catalog()


def test_every_catalog_entry_has_required_fields_and_types():
    assert SOURCE_CATALOG

    for metadata in SOURCE_CATALOG.values():
        assert REQUIRED_FIELDS <= metadata.keys()
        assert isinstance(metadata["group"], SourceGroup)
        assert isinstance(metadata["source_type"], SourceType)
        assert type(metadata["enabled"]) is bool
        assert type(metadata["recommended_for_mvp"]) is bool
        assert type(metadata["priority"]) is int


def test_get_enabled_sources_returns_only_enabled_sources():
    sources = get_enabled_sources()

    assert sources
    assert all(SOURCE_CATALOG[source]["enabled"] for source in sources)
    assert set(sources) == {
        source
        for source, metadata in SOURCE_CATALOG.items()
        if metadata["enabled"]
    }


def test_get_enabled_sources_is_sorted_by_descending_priority():
    sources = get_enabled_sources()
    actual_order = [
        (SOURCE_CATALOG[source]["priority"], source) for source in sources
    ]
    expected_order = sorted(
        actual_order,
        key=lambda item: (-item[0], item[1]),
    )

    assert actual_order == expected_order


@pytest.mark.parametrize("group", list(SourceGroup))
def test_get_enabled_sources_filters_by_source_group(group):
    sources = get_enabled_sources(group=group)

    assert sources == expected_enabled_sources(group)
    assert all(SOURCE_CATALOG[source]["group"] == group for source in sources)


def test_mvp_only_excludes_non_recommended_sources():
    sources = get_enabled_sources(mvp_only=True)

    assert sources == expected_enabled_sources(mvp_only=True)
    assert all(
        SOURCE_CATALOG[source]["recommended_for_mvp"] for source in sources
    )
    assert not {
        source
        for source, metadata in SOURCE_CATALOG.items()
        if metadata["enabled"] and not metadata["recommended_for_mvp"]
    } & set(sources)


def test_group_none_returns_enabled_sources_from_all_groups():
    sources = get_enabled_sources(group=None)
    expected_groups = {
        metadata["group"]
        for metadata in SOURCE_CATALOG.values()
        if metadata["enabled"]
    }

    assert sources == expected_enabled_sources()
    assert {SOURCE_CATALOG[source]["group"] for source in sources} == expected_groups


@pytest.mark.parametrize(
    ("source", "expected_group"),
    [
        ("UKRAINE_ODOO_COMPANIES", SourceGroup.ODOO_UKRAINE),
        ("ODOO_JOBS", SourceGroup.ODOO_WORLD),
        ("DOU", SourceGroup.UKRAINE),
        ("DJINNI", SourceGroup.UKRAINE),
        ("WORKUA", SourceGroup.UKRAINE),
        ("HAPPYMONDAY", SourceGroup.UKRAINE),
        ("LINKEDIN", SourceGroup.WORLD_JOB_BOARDS),
        ("INDEED", SourceGroup.WORLD_JOB_BOARDS),
    ],
)
def test_known_sources_belong_to_expected_group_when_present(
    source, expected_group
):
    if source not in SOURCE_CATALOG:
        pytest.skip(f"{source} is not present in the current source catalog")

    assert SOURCE_CATALOG[source]["group"] == expected_group
