from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from services.storage import products
import os

async def admin_panel_handler(message: types.Message):
    if message.from_user.id == int(os.getenv("ADMIN_ID")):
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")],
            [InlineKeyboardButton(text="✏️ Изменить товар", callback_data="edit_product")],
            [InlineKeyboardButton(text="📜 Показать товары", callback_data="show_products")]
        ])
        await message.answer("Добро пожаловать в админ-панель!", reply_markup=admin_keyboard)
    else:
        await message.answer("У вас нет доступа к админ-панели.")

async def add_product_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Введите название товара:")
async def show_products_handler(callback_query: types.CallbackQuery):
    if products:
        response = "\n".join(
            [f"📦 {name} — {details['price']} USD\n{details['description']}" for name, details in products.items()]
        )
    else:
        response = "Список товаров пуст."
    await callback_query.message.answer(response)

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_panel_handler, Command("admin_panel"))
    dp.callback_query.register(add_product_handler, lambda c: c.data == "add_product")
    dp.callback_query.register(show_products_handler, lambda c: c.data == "show_products")
