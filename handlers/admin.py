from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from services.storage import Storage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.states import AddItemState, EditItemState

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

async def edit_item_handler(message: types.Message, state: FSMContext):
    categories = storage.get_categories()
    if not categories:
        await message.answer("Категории товаров отсутствуют.")
        return

    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f"edit_category_{category}"))
    
    await message.answer("Выберите категорию для редактирования товара:", reply_markup=keyboard.as_markup())
    await state.set_state(EditItemState.waiting_for_category)

async def edit_item_category_handler(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.replace("edit_category_", "")
    items = storage.get_items_by_category(category)
    
    if not items:
        await callback_query.message.answer(f"В категории '{category}' нет товаров.")
        return

    response = f"Выберите ID товара для редактирования (категория '{category}'):\n\n"
    for item in items:
        response += f"🆔 {item['id']} | {item['name']} | {item['price']} USD | {item['quantity']} шт.\nОписание: {item['description']}\n\n"

    await callback_query.message.answer(response)
    await state.update_data(category=category)
    await state.set_state(EditItemState.waiting_for_item_id)

async def edit_item_id_handler(message: types.Message, state: FSMContext):
    try:
        item_id = int(message.text)
        data = await state.get_data()
        category = data["category"]
        item = storage.get_item(category, item_id)

        if item:
            await state.update_data(item_id=item_id)
            await message.answer(
                f"Редактируем товар:\n"
                f"🔹 Название: {item['name']}\n"
                f"💰 Цена: {item['price']} USD\n"
                f"📦 Количество: {item['quantity']}\n"
                f"📝 Описание: {item['description']}\n\n"
                f"Введите новые данные в формате:\n"
                f"`Название;Цена;Количество;Описание`", parse_mode="Markdown"
            )
            await state.set_state(EditItemState.waiting_for_new_data)
        else:
            await message.answer("Ошибка! Товар с таким ID не найден.")
    except ValueError:
        await message.answer("Ошибка! Введите корректный ID.")

async def edit_item_save_handler(message: types.Message, state: FSMContext):
    try:
        name, price, quantity, description = map(str.strip, message.text.split(";"))
        price = float(price)
        quantity = int(quantity)

        data = await state.get_data()
        category = data["category"]
        item_id = data["item_id"]

        success = storage.edit_item(category, item_id, name, price, quantity, description)
        if success:
            await message.answer(f"✅ Товар с ID {item_id} успешно обновлён!")
        else:
            await message.answer("Ошибка! Не удалось обновить товар.")
    except ValueError:
        await message.answer("Ошибка! Введите корректные данные в формате: `Название;Цена;Количество;Описание`.")
    finally:
        await state.clear()

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_panel_handler, Command("admin_panel"))
    dp.message.register(add_item_handler, Command("add_item"))
    dp.message.register(item_category_handler, StateFilter(AddItemState.waiting_for_category))
    dp.message.register(item_name_handler, StateFilter(AddItemState.waiting_for_name))
    dp.message.register(item_price_handler, StateFilter(AddItemState.waiting_for_price))
    dp.message.register(item_description_handler, StateFilter(AddItemState.waiting_for_description))
    dp.message.register(item_quantity_handler, StateFilter(AddItemState.waiting_for_quantity))
    dp.message.register(view_items_handler, Command("view_items"))
    dp.message.register(edit_item_handler, Command("edit_item"))
    dp.callback_query.register(edit_item_category_handler, lambda cb: cb.data.startswith("edit_category_"))
    dp.message.register(edit_item_id_handler, StateFilter(EditItemState.waiting_for_item_id))
    dp.message.register(edit_item_save_handler, StateFilter(EditItemState.waiting_for_new_data))
