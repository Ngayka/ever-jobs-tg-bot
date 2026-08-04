from enum import StrEnum

from app.job_sources import SourceType


class SourceSelection(StrEnum):
    JOB_BOARDS = "job_boards"
    COMPANIES = "companies"
    ALL = "all"


def get_source_types(
    selection: SourceSelection,
) -> set[SourceType]:
    if selection == SourceSelection.JOB_BOARDS:
        return {
            SourceType.JOB_BOARD,
            SourceType.REMOTE_JOB_BOARD,
            SourceType.GOVERNMENT,
            SourceType.NICHE,
            SourceType.FREELANCE,
        }

    if selection == SourceSelection.COMPANIES:
        return {
            SourceType.COMPANY,
        }

    return {
        SourceType.JOB_BOARD,
        SourceType.REMOTE_JOB_BOARD,
        SourceType.GOVERNMENT,
        SourceType.NICHE,
        SourceType.COMPANY,
        SourceType.FREELANCE,
    }