from aiogram.fsm.state import State, StatesGroup


class AddState(StatesGroup):
    price = State()
    name = State()