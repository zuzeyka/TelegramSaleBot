from aiogram import Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command

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

    dp.message.register(start_handler, Command("start"))

