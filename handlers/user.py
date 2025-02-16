from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import FSInputFile  
from aiogram.filters import Command
from services.storage import Storage
from services.user import UserManager
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from services.states import BuyItemState

storage = Storage()
user_manager = UserManager()

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
        user_id = message.from_user.id
        username = message.from_user.username
    
        user_manager.create_user(user_id, username)
        await message.answer(f"Hello, {message.from_user.full_name}!", reply_markup=keyboard)

    async def profile_handler(message: types.Message):
        user_id = message.from_user.id
        
        balance = user_manager.get_balance(user_id)
        orders = user_manager.get_orders(user_id)
    
        response = f"👤 **Ваш профиль**\n"
        response += f"💰 **Баланс:** {balance:.2f} USD\n"
        response += f"📜 **История покупок:**\n"
    
        if orders:
            for order in orders[-5:]:
                response += f"🔹 {order['item_name']} ({order['category']}) — {order['quantity']} шт. на {order['total_price']:.2f} USD\n"
                response += f"📅 {order['date']}\n\n"
        else:
            response += "❌ Нет заказов.\n"
    
        await message.answer(response, parse_mode="Markdown")

    async def availability_handler(message: types.Message):
        all_items = storage.get_all_items()
        if not all_items:
            await message.answer("Список товаров пуст.")
            return

        response = "📦 **Наличие товаров:**\n\n"
        for item in all_items:
            response += (
                f"🔹**Название:** **{item['name']}**\n"
                f"📦 **Остаток:** {item['quantity']} шт.\n\n"
            )

        await message.answer(response, parse_mode="Markdown")
    
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
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        category = callback_query.data.replace("category_", "")
        items = storage.get_items_by_category(category)

        if not items:
            await callback_query.message.answer(f"В категории '{category}' нет товаров.")
            return

        keyboard = InlineKeyboardBuilder()
        for item in items:
            keyboard.add(types.InlineKeyboardButton(text=item["name"], callback_data=f"item_{category}_{item['id']}"))

        keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories"))

        await callback_query.message.answer(f"Товары в категории '{category}':", reply_markup=keyboard.as_markup())

    async def show_items_handler(callback_query: types.CallbackQuery):
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
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
            caption=f"🔹 {item['name']}\n💰 Цена: {item['price']:.2f} USD\n📦 Остаток: {item['quantity']} шт.\n📝 {item['description']}",
            reply_markup=keyboard.as_markup()
        )

    async def back_to_categories_handler(callback_query: types.CallbackQuery):
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        await show_categories_handler(callback_query.message)

    async def back_to_category_handler(callback_query: types.CallbackQuery):
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        category = callback_query.data.replace("back_to_category_", "")
        new_callback_query = types.CallbackQuery(
            id=callback_query.id,
            from_user=callback_query.from_user,
            message=callback_query.message,
            chat_instance=callback_query.chat_instance,
            data=f"category_{category}"
        )
        await show_items_in_category_handler(new_callback_query)

    async def buy_item_handler(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        _, category, item_id = callback_query.data.split("_")
        item_id = int(item_id)
        item = storage.get_item(category, item_id)

        if not item:
            await callback_query.message.answer("Ошибка! Товар не найден.")
            return

        await state.update_data(category=category, item_id=item_id)
        
        keyboard = InlineKeyboardBuilder()
        for i in range(1, 11):
            keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f"quantity_{i}"))
        keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_category_{category}"))

        await callback_query.message.answer(f"Выберите количество товара '{item['name']}' (доступно {item['quantity']} шт.):", reply_markup=keyboard.as_markup())
        await state.set_state(BuyItemState.waiting_for_quantity)

    async def buy_item_quantity_handler(callback_query: types.CallbackQuery, state: FSMContext):
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
        quantity = int(callback_query.data.replace("quantity_", ""))
        data = await state.get_data()
        category = data["category"]
        item_id = data["item_id"]
        item = storage.get_item(category, item_id)
        user_id = callback_query.from_user.id

        if quantity <= 0:
            await callback_query.message.answer("Ошибка! Введите корректное количество (больше нуля).")
            return

        if quantity > item["quantity"]:
            await callback_query.message.answer(f"Ошибка! Доступно только {item['quantity']} шт.")
            return

        total_price = item["price"] * quantity

        if user_manager.get_balance(user_id) < total_price:
            await callback_query.message.answer("Недостаточно средств.")
            return

        user_manager.subtract_balance(user_id, total_price)
        user_manager.add_order(user_id, {
            "item_name": item["name"],
            "category": category,
            "price": item["price"],
            "quantity": quantity,
            "total_price": total_price,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        storage.change_item_quantity(category, item_id, quantity)
        await callback_query.message.answer(f"Вы купили {quantity} шт. товара '{item['name']}' за {total_price:.2f} USD.")
        await state.clear()

    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(show_items_in_category_handler, lambda cb: cb.data.startswith("category_"))
    dp.callback_query.register(show_items_handler, lambda cb: cb.data.startswith("item_"))
    dp.callback_query.register(back_to_categories_handler, lambda cb: cb.data == "back_to_categories")
    dp.callback_query.register(back_to_category_handler, lambda cb: cb.data.startswith("back_to_category_"))
    dp.callback_query.register(buy_item_handler, lambda cb: cb.data.startswith("buy_"))
    dp.callback_query.register(buy_item_quantity_handler, lambda cb: cb.data.startswith("quantity_"))
    dp.message.register(show_categories_handler, lambda msg: msg.text == "📖 Все товары")
    dp.message.register(availability_handler, lambda msg: msg.text == "📝 Наличие товаров")
    dp.message.register(about_handler, lambda msg: msg.text == "💡 О магазине")
    dp.message.register(profile_handler, lambda msg: msg.text == "👤 Профиль")
    dp.message.register(rules_handler, lambda msg: msg.text == "📜 Правила")
    dp.message.register(help_handler, lambda msg: msg.text == "❤️ Помощь")