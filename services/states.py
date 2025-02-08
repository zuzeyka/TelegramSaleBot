from aiogram.fsm.state import StatesGroup, State

class AddItemState(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_quantity = State()
    waiting_for_image = State()

class EditItemState(StatesGroup):
    waiting_for_category = State()
    waiting_for_item_id = State()
    waiting_for_new_data = State()
