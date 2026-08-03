from aiogram.filters.callback_data import CallbackData


class VacancyActionCallback(
    CallbackData,
    prefix="vacancy",
):
    action: str
    vacancy_id: int
