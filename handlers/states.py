from aiogram.fsm.state import State, StatesGroup


class AddState(StatesGroup):
    price = State()
    name = State()
    
class RevenueForm(StatesGroup):
    amount = State()
    description = State()
    
class ExpenseForm(StatesGroup):
    amount = State()
    description = State()