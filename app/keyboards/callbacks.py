from aiogram.filters.callback_data import CallbackData


class VacancyActionCallback(
    CallbackData,
    prefix="vacancy",
):
    action: str
    vacancy_id: int


class SearchNavigationCallback(
    CallbackData,
    prefix="search_nav",
):
    action: str


class RegionCallback(
    CallbackData,
    prefix="region",
):
    region: str


class SourceTypeCallback(
    CallbackData,
    prefix="source_type",
):
    source_type: str