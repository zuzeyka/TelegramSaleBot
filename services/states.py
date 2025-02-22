from aiogram.fsm.state import StatesGroup, State

class AddItemState(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_quantity = State()
    waiting_for_image = State()
    waiting_for_delete_category = State()
    waiting_for_delete_item = State()

class EditItemState(StatesGroup):
    waiting_for_category = State()
    waiting_for_item_id = State()
    waiting_for_property_choice = State()
    waiting_for_new_value = State()
    waiting_for_new_image = State()

class CategoryState(StatesGroup):
    waiting_for_rename_category = State()
    waiting_for_new_category_name = State()
    waiting_for_delete_category = State()
    waiting_for_delete_or_transfer = State()
    waiting_for_transfer_category = State()

class BuyItemState(StatesGroup):
    waiting_for_quantity = State()

class TopUpBalanceState(StatesGroup):
    waiting_for_amount = State()
