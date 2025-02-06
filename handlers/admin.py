from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from services.storage import Storage
from services.states import AddItemState

storage = Storage()

async def admin_panel_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать в админ-панель!\n"
        "Доступные команды:\n"
        "/add_item - Добавить товар\n"
        "/edit_item - Изменить товар\n"
        "/view_items - Просмотреть все товары"
    )

async def add_item_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите категорию товара:")
    await state.set_state(AddItemState.waiting_for_category)

async def item_category_handler(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите название товара:")
    await state.set_state(AddItemState.waiting_for_name)

async def item_name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену товара (только число):")
    await state.set_state(AddItemState.waiting_for_price)

async def item_price_handler(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Введите количество товара:")
        await state.set_state(AddItemState.waiting_for_quantity)
    except ValueError:
        await message.answer("Ошибка! Введите корректную цену.")

async def item_quantity_handler(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        await state.update_data(quantity=quantity)
        await message.answer("Введите описание товара:")
        await state.set_state(AddItemState.waiting_for_description)
    except ValueError:
        await message.answer("Ошибка! Введите корректное количество (только число).")

async def item_description_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    name = data["name"]
    price = data["price"]
    quantity = data["quantity"]
    description = message.text

    storage.add_item(category, name, price, quantity, description)
    await message.answer(f"Товар '{name}' добавлен в категорию '{category}'!")
    await state.clear()


async def view_items_handler(message: types.Message):
    items = storage.get_all_items()
    if items:
        response = "\n".join(
            [f"ID: {item['id']} | {item['name']} — {item['price']} USD\nОписание: {item['description']}" for item in items]
        )
    else:
        response = "Список товаров пуст."
    await message.answer(response)

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_panel_handler, Command("admin_panel"))
    dp.message.register(add_item_handler, Command("add_item"))
    dp.message.register(item_category_handler, StateFilter(AddItemState.waiting_for_category))
    dp.message.register(item_name_handler, StateFilter(AddItemState.waiting_for_name))
    dp.message.register(item_price_handler, StateFilter(AddItemState.waiting_for_price))
    dp.message.register(item_description_handler, StateFilter(AddItemState.waiting_for_description))
    dp.message.register(item_quantity_handler, StateFilter(AddItemState.waiting_for_quantity))
    dp.message.register(view_items_handler, Command("view_items"))
