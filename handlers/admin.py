from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from services.storage import Storage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.states import AddItemState, EditItemState
import os

storage = Storage()

async def admin_panel_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать в админ-панель!\n"
        "Доступные команды:\n"
        "/add_item - Добавить товар\n"
        "/delete_item - Удалить товар\n"
        "/edit_item - Изменить товар\n"
        "/view_items - Просмотреть все товары"
    )

async def add_item_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите категорию товара:")
    await state.set_state(AddItemState.waiting_for_category)

async def delete_item_handler(message: types.Message, state: FSMContext):
    categories = storage.get_categories()
    if not categories:
        await message.answer("Категории товаров отсутствуют.")
        return

    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f"delete_category_{category}"))
    
    await message.answer("Выберите категорию для удаления товара:", reply_markup=keyboard.as_markup())
    await state.set_state(AddItemState.waiting_for_delete_category)

async def delete_item_category_handler(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.replace("delete_category_", "")
    items = storage.get_items_by_category(category)
    
    if not items:
        await callback_query.message.answer(f"В категории '{category}' нет товаров.")
        return

    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.add(types.InlineKeyboardButton(text=item["name"], callback_data=f"delete_item_{category}_{item['id']}"))

    await callback_query.message.answer(f"Выберите товар для удаления (категория '{category}'):", reply_markup=keyboard.as_markup())
    await state.update_data(category=category)
    await state.set_state(AddItemState.waiting_for_delete_item)

async def delete_item_confirm_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.replace("delete_item_", "").split("_")
    print(data, len(data))
    if len(data) != 2:
        await callback_query.message.answer("Ошибка! Неверный формат данных.")
        return

    category, item_id = data
    item_id = int(item_id)
    success = storage.delete_item(category, item_id)

    if success:
        await callback_query.message.answer(f"✅ Товар с ID {item_id} успешно удален!")
    else:
        await callback_query.message.answer("Ошибка! Не удалось удалить товар.")
    await state.clear()

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
    await state.update_data(description=message.text)
    await message.answer("Отправьте изображение товара (фото).")
    await state.set_state(AddItemState.waiting_for_image)

async def item_image_handler(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Ошибка! Отправьте изображение, а не текст.")
        return

    data = await state.get_data()
    category = data["category"]
    name = data["name"]
    price = data["price"]
    quantity = data["quantity"]
    description = data["description"]

    bot = message.bot

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path

    image_filename = f"{name.replace(' ', '_')}.jpg"
    local_path = os.path.join(storage.image_folder, image_filename)
    await bot.download_file(file_path, local_path)

    storage.add_item(category, name, price, quantity, description, local_path)
    await message.answer(f"✅ Товар '{name}' добавлен в категорию '{category}'!")
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
            keyboard = InlineKeyboardBuilder()
            keyboard.add(types.InlineKeyboardButton(text="Название", callback_data="edit_name"))
            keyboard.add(types.InlineKeyboardButton(text="Цену", callback_data="edit_price"))
            keyboard.add(types.InlineKeyboardButton(text="Количество", callback_data="edit_quantity"))
            keyboard.add(types.InlineKeyboardButton(text="Описание", callback_data="edit_description"))
            keyboard.add(types.InlineKeyboardButton(text="Изображение", callback_data="edit_image"))
            keyboard.adjust(2)

            await message.answer(
                f"Редактируем товар:\n"
                f"🔹 Название: {item['name']}\n"
                f"💰 Цена: {item['price']} USD\n"
                f"📦 Количество: {item['quantity']}\n"
                f"📝 Описание: {item['description']}\n\n"
                f"Выберите, что вы хотите изменить:", reply_markup=keyboard.as_markup()
            )
            await state.set_state(EditItemState.waiting_for_property_choice)
        else:
            await message.answer("Ошибка! Товар с таким ID не найден.")
    except ValueError:
        await message.answer("Ошибка! Введите корректный ID.")

async def edit_item_property_choice_handler(callback_query: types.CallbackQuery, state: FSMContext):
    property_choice = callback_query.data.replace("edit_", "")
    await state.update_data(property_choice=property_choice)
    if property_choice == "image":
        await callback_query.message.answer("Отправьте новое изображение товара.")
        await state.set_state(EditItemState.waiting_for_new_image)
    else:
        await callback_query.message.answer(f"Введите новое значение для {property_choice}.")
        await state.set_state(EditItemState.waiting_for_new_value)

async def edit_item_save_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    item_id = data["item_id"]
    property_choice = data["property_choice"]

    try:
        if property_choice == "price":
            new_value = float(message.text)
        elif property_choice == "quantity":
            new_value = int(message.text)
        else:
            new_value = message.text.strip()

        success = storage.edit_item_property(category, item_id, property_choice, new_value)
        if success:
            await message.answer(f"✅ {property_choice.capitalize()} товара с ID {item_id} успешно обновлено!")
        else:
            await message.answer(f"Ошибка! Не удалось обновить {property_choice} товара.")
    except ValueError:
        await message.answer(f"Ошибка! Введите корректное значение для {property_choice}.")
    finally:
        await state.clear()

async def edit_item_image_handler(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Ошибка! Отправьте изображение, а не текст.")
        return

    data = await state.get_data()
    category = data["category"]
    item_id = data["item_id"]
    item = storage.get_item(category, item_id)

    bot = message.bot

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path

    image_filename = f"{item['name'].replace(' ', '_')}.jpg"
    local_path = os.path.join(storage.image_folder, image_filename)
    await bot.download_file(file_path, local_path)

    success = storage.edit_item_image(category, item_id, local_path)
    if success:
        await message.answer(f"✅ Изображение товара с ID {item_id} успешно обновлено!")
    else:
        await message.answer("Ошибка! Не удалось обновить изображение товара.")
    await state.clear()

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_panel_handler, Command("admin_panel"))
    dp.message.register(add_item_handler, Command("add_item"))
    dp.message.register(delete_item_handler, Command("delete_item"))
    dp.callback_query.register(delete_item_category_handler, lambda cb: cb.data.startswith("delete_category_"))
    dp.callback_query.register(delete_item_confirm_handler, lambda cb: cb.data.startswith("delete_item_"))
    dp.message.register(item_category_handler, StateFilter(AddItemState.waiting_for_category))
    dp.message.register(item_name_handler, StateFilter(AddItemState.waiting_for_name))
    dp.message.register(item_price_handler, StateFilter(AddItemState.waiting_for_price))
    dp.message.register(item_description_handler, StateFilter(AddItemState.waiting_for_description))
    dp.message.register(item_quantity_handler, StateFilter(AddItemState.waiting_for_quantity))
    dp.message.register(item_image_handler, StateFilter(AddItemState.waiting_for_image))
    dp.message.register(view_items_handler, Command("view_items"))
    dp.message.register(edit_item_handler, Command("edit_item"))
    dp.callback_query.register(edit_item_category_handler, lambda cb: cb.data.startswith("edit_category_"))
    dp.message.register(edit_item_id_handler, StateFilter(EditItemState.waiting_for_item_id))
    dp.callback_query.register(edit_item_property_choice_handler, StateFilter(EditItemState.waiting_for_property_choice))
    dp.message.register(edit_item_save_handler, StateFilter(EditItemState.waiting_for_new_value))
    dp.message.register(edit_item_image_handler, StateFilter(EditItemState.waiting_for_new_image))
