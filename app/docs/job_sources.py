"""Compact standalone source catalog for the JobNest Telegram bot."""

from enum import StrEnum
from tokenize import group


class SourceGroup(StrEnum):
    UKRAINE = "ukraine"
    ODOO_UKRAINE = "odoo_ukraine"
    ODOO_WORLD = "odoo_world"
    JOB_BOARDS_WW = "world_job_boards"
    LINKEDIN = "linkedin"
    REMOTEFIRSTJOBS = "remote_first_jobs"


class SourceType(StrEnum):
    JOB_BOARD = "job_board"
    COMPANY_GROUP = "company_group"
    OFFICIAL_CAREERS = "official_careers"
    REMOTE_JOB_BOARD = "remote_job_board"


SourceMetadata = dict[str, SourceGroup | SourceType | bool | int]


SOURCE_CATALOG: dict[str, SourceMetadata] = {
    "DOU": {
        "group": SourceGroup.UKRAINE,
        "source_type": SourceType.JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 100,
    },
    "DJINNI": {
        "group": SourceGroup.UKRAINE,
        "source_type": SourceType.JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 95,
    },
    "WORKUA": {
        "group": SourceGroup.UKRAINE,
        "source_type": SourceType.JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 90,
    },
    "HAPPYMONDAY": {
        "group": SourceGroup.UKRAINE,
        "source_type": SourceType.JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 80,
    },
    "UKRAINE_ODOO_COMPANIES": {
        "group": SourceGroup.ODOO_UKRAINE,
        "source_type": SourceType.COMPANY_GROUP,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 110,
    },
    "ODOO_JOBS": {
        "group": SourceGroup.ODOO_WORLD,
        "source_type": SourceType.OFFICIAL_CAREERS,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 105,
    },
    "LINKEDIN": {
        "group": SourceGroup.LINKEDIN,
        "source_type": SourceType.JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 80,
    },
    # "INDEED": {
    #     "group": SourceGroup.WORLD_JOB_BOARDS,
    #     "source_type": SourceType.JOB_BOARD,
    #     "enabled": True,
    #     "recommended_for_mvp": True,
    #     "priority": 100,
    # },
    "GLASSDOOR": {
        "group": SourceGroup.JOB_BOARDS_WW,
        "source_type": SourceType.JOB_BOARD,
        "enabled": False,
        "recommended_for_mvp": True,
        "priority": 90,
    },
    "WELLFOUND": {
        "group": SourceGroup.JOB_BOARDS_WW,
        "source_type": SourceType.JOB_BOARD,
        "enabled": False,
        "recommended_for_mvp": True,
        "priority": 80,
    },
    "WEWORKREMOTELY": {
        "group": SourceGroup.JOB_BOARDS_WW,
        "source_type": SourceType.REMOTE_JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 80,
    },
    "REMOTEOK": {
        "group": SourceGroup.JOB_BOARDS_WW,
        "source_type": SourceType.REMOTE_JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 75,
    },
    "PYJOBS": {
        'group': SourceGroup.JOB_BOARDS_WW,
        "source_type": SourceType.REMOTE_JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 80,
    },
    "REMOTEFIRSTJOBS": {
        'group': SourceGroup.REMOTEFIRSTJOBS,
        "source_type": SourceType.REMOTE_JOB_BOARD,
        "enabled": True,
        "recommended_for_mvp": True,
        "priority": 80,
    }
}


def get_enabled_sources(
    group: SourceGroup | None = None,
    *,
    mvp_only: bool = False,
) -> list[str]:
    """Return enabled source keys ordered by descending priority."""
    sources = [
        source
        for source, metadata in SOURCE_CATALOG.items()
        if metadata["enabled"] is True
        and (group is None or metadata["group"] == group)
        and (
            not mvp_only
            or metadata["recommended_for_mvp"] is True
        )
    ]

    return sorted(
        sources,
        key=lambda source: (
            -int(SOURCE_CATALOG[source]["priority"]),
            source,
        ),
    )


def validate_source_catalog() -> None:
    """Raise an error when a catalog entry violates the public contract."""
    required_fields = {
        "group",
        "source_type",
        "enabled",
        "recommended_for_mvp",
        "priority",
    }

    for source, metadata in SOURCE_CATALOG.items():
        missing_fields = required_fields - metadata.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"{source} is missing required fields: {missing}")

        if not isinstance(metadata["group"], SourceGroup):
            raise TypeError(f"{source}.group must be a SourceGroup")

        if not isinstance(metadata["source_type"], SourceType):
            raise TypeError(f"{source}.source_type must be a SourceType")

        if type(metadata["enabled"]) is not bool:
            raise TypeError(f"{source}.enabled must be bool")

        if type(metadata["recommended_for_mvp"]) is not bool:
            raise TypeError(
                f"{source}.recommended_for_mvp must be bool"
            )

        if type(metadata["priority"]) is not int:
            raise TypeError(f"{source}.priority must be int")


validate_source_catalog()
