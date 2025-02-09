from aiogram import Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import FSInputFile  
from aiogram.filters import Command
from services.storage import Storage

storage = Storage()

def register_handlers_user(dp: Dispatcher):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📖 Все товары"))
    builder.add(types.KeyboardButton(text="📝 Наличие товаров"))
    builder.add(types.KeyboardButton(text="💡 О магазине"))
    builder.add(types.KeyboardButton(text="👤 Профиль"))
    builder.add(types.KeyboardButton(text="📜 Правила"))
    builder.add(types.KeyboardButton(text="❤️ Помощь"))
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)

    async def start_handler(message: types.Message):
        await message.answer(f"Hello, {message.from_user.full_name}!", reply_markup=keyboard)

    async def profile_handler(message: types.Message):
        user_id = message.from_user.id
        await message.answer(f"Ваш Telegram ID: `{user_id}`", parse_mode="Markdown")

    async def availability_handler(message: types.Message):
        await message.answer("Доступные товары")
    
    async def about_handler(message: types.Message):
        await message.answer("Описание сайта. Создан @zuzeyka")

    async def help_handler(message: types.Message):
        await message.answer("Поддержка: @JacobHarrison")

    async def rules_handler(message: types.Message):
        await message.answer(f"1. Незнание правил не освобождает от ответственности.\n2. Возврат средств возмещается только по решению администрации и только на баланс бота.\n3. Выдача товара может занимать до 15 суток.\n4. За спам, оскорбления и т. п. продавец в праве отказать в выдаче товара.\n5. Если на текущий день лимит по лайкам закончился, то вы будете в начале очереди на следующий день.\n6. Клиент имеет право запросить возврат средств, если услуга не может быть оказана по какой-либо действительно проблемной причине.")

    async def show_categories_handler(message: types.Message):
        categories = storage.get_categories()
        if not categories:
            await message.answer("Категории товаров отсутствуют.")
            return

        keyboard = InlineKeyboardBuilder()
        for category in categories:
            keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f"category_{category}"))

        await message.answer("Выберите категорию:", reply_markup=keyboard.as_markup())

    async def show_items_in_category_handler(callback_query: types.CallbackQuery):
        category = callback_query.data.replace("category_", "")
        items = storage.get_items_by_category(category)

        if not items:
            await callback_query.message.answer(f"В категории '{category}' нет товаров.")
            return

        keyboard = InlineKeyboardBuilder()
        for item in items:
            keyboard.add(types.InlineKeyboardButton(text=item["name"], callback_data=f"item_{category}_{item['id']}"))

        keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories"))

        if callback_query.message.text:
            await callback_query.message.edit_text(f"Товары в категории '{category}':", reply_markup=keyboard.as_markup())
        else:
            await callback_query.message.answer(f"Товары в категории '{category}':", reply_markup=keyboard.as_markup())

    async def show_items_handler(callback_query: types.CallbackQuery):
        _, category, item_id = callback_query.data.split("_")
        item_id = int(item_id)
        item = storage.get_item(category, item_id)

        if not item:
            await callback_query.message.answer("Ошибка! Товар не найден.")
            return

        keyboard = InlineKeyboardBuilder()
        keyboard.add(types.InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy_{category}_{item_id}"))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_category_{category}"))

        photo = FSInputFile(item["image_path"])

        await callback_query.message.answer_photo(
            photo=photo,
            caption=f"🔹 {item['name']}\n💰 Цена: {item['price']} USD\n📦 Остаток: {item['quantity']} шт.\n📝 {item['description']}",
            reply_markup=keyboard.as_markup()
        )

    async def back_to_categories_handler(callback_query: types.CallbackQuery):
        await show_categories_handler(callback_query.message)

    async def back_to_category_handler(callback_query: types.CallbackQuery):
        category = callback_query.data.replace("back_to_category_", "")
        new_callback_query = types.CallbackQuery(
            id=callback_query.id,
            from_user=callback_query.from_user,
            message=callback_query.message,
            chat_instance=callback_query.chat_instance,
            data=f"category_{category}"
        )
        await show_items_in_category_handler(new_callback_query)

    async def buy_item_handler(callback_query: types.CallbackQuery):
        _, category, item_id = callback_query.data.split("_")
        item_id = int(item_id)
        item = storage.get_item(category, item_id)

        if not item:
            await callback_query.message.answer("Ошибка! Товар не найден.")
            return

        # Implement the buying logic here
        await callback_query.message.answer(f"Вы купили товар '{item['name']}' за {item['price']} USD.")

    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(show_items_in_category_handler, lambda cb: cb.data.startswith("category_"))
    dp.callback_query.register(show_items_handler, lambda cb: cb.data.startswith("item_"))
    dp.callback_query.register(back_to_categories_handler, lambda cb: cb.data == "back_to_categories")
    dp.callback_query.register(back_to_category_handler, lambda cb: cb.data.startswith("back_to_category_"))
    dp.callback_query.register(buy_item_handler, lambda cb: cb.data.startswith("buy_"))
    dp.message.register(show_categories_handler, lambda msg: msg.text == "📖 Все товары")
    dp.message.register(availability_handler, lambda msg: msg.text == "📝 Наличие товаров")
    dp.message.register(about_handler, lambda msg: msg.text == "💡 О магазине")
    dp.message.register(profile_handler, lambda msg: msg.text == "👤 Профиль")
    dp.message.register(rules_handler, lambda msg: msg.text == "📜 Правила")
    dp.message.register(help_handler, lambda msg: msg.text == "❤️ Помощь")