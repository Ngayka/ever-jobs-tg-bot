from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    waiting_for_search_term = State()
    waiting_for_region = State()
    waiting_for_source_type = State()
    browsing_results = State()
    waiting_for_location = State()