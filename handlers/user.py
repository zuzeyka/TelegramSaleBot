from aiogram import Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
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

    async def goods_handler(message: types.Message):
        categories = storage.get_categories()
        if not categories:
            await message.answer("Категории товаров отсутствуют.")
            return

        keyboard = InlineKeyboardBuilder()
        for category in categories:
            keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f"category_{category}"))
        
        await message.answer("Выберите категорию:", reply_markup=keyboard.as_markup())
    
    async def availability_handler(message: types.Message):
        await message.answer("Доступные товары")
    
    async def about_handler(message: types.Message):
        await message.answer("Описание сайта. Создан @zuzeyka")

    async def help_handler(message: types.Message):
        await message.answer("Поддержка: @JacobHarrison")

    async def rules_handler(message: types.Message):
        await message.answer(f"1. Незнание правил не освобождает от ответственности.\n2. Возврат средств возмещается только по решению администрации и только на баланс бота.\n3. Выдача товара может занимать до 15 суток.\n4. За спам, оскорбления и т. п. продавец в праве отказать в выдаче товара.\n5. Если на текущий день лимит по лайкам закончился, то вы будете в начале очереди на следующий день.\n6. Клиент имеет право запросить возврат средств, если услуга не может быть оказана по какой-либо действительно проблемной причине.")

    async def show_items_handler(callback_query: types.CallbackQuery):
        category = callback_query.data.replace("category_", "")
        items = storage.get_items_by_category(category)
        
        if not items:
            await callback_query.message.answer(f"В категории '{category}' нет товаров.")
            return

        response = f"Товары в категории '{category}':\n\n"
        for item in items:
            response += f"🔹 {item['name']} | {item['price']} USD | Количество: {item['quantity']}\nОписание: {item['description']}\n\n"
        
        await callback_query.message.answer(response)
    
    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(show_items_handler, lambda cb: cb.data.startswith("category_"))
    dp.message.register(goods_handler, lambda msg: msg.text == "📖 Все товары")
    dp.message.register(availability_handler, lambda msg: msg.text == "📝 Наличие товаров")
    dp.message.register(about_handler, lambda msg: msg.text == "💡 О магазине")
    dp.message.register(profile_handler, lambda msg: msg.text == "👤 Профиль")
    dp.message.register(rules_handler, lambda msg: msg.text == "📜 Правила")
    dp.message.register(help_handler, lambda msg: msg.text == "❤️ Помощь")