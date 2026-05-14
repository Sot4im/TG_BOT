import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
import app.keyboards as kb
from app.database import db
from config import ADMIN_ID
from datetime import datetime, timedelta
import re

router = Router()
logger = logging.getLogger(__name__)


class OrderStates(StatesGroup):
    choosing_delivery = State()
    entering_address = State()
    choosing_date = State()  # Теперь пользователь сам вводит дату
    entering_time = State()
    confirming = State()


def validate_date(date_string: str) -> bool:
    """Проверка корректности даты"""
    # Поддерживаемые форматы: ДД.ММ.ГГГГ или ДД-ММ-ГГГГ или ДД/ММ/ГГГГ
    patterns = [
        r'^(\d{2})\.(\d{2})\.(\d{4})$',  # 31.12.2024
        r'^(\d{2})-(\d{2})-(\d{4})$',  # 31-12-2024
        r'^(\d{2})/(\d{2})/(\d{4})$',  # 31/12/2024
        r'^(\d{4})-(\d{2})-(\d{2})$',  # 2024-12-31
    ]

    for pattern in patterns:
        match = re.match(pattern, date_string)
        if match:
            if pattern == r'^(\d{4})-(\d{2})-(\d{2})$':
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            else:
                day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))

            # Проверяем, существует ли такая дата
            try:
                date_obj = datetime(year, month, day)
                # Проверяем, что дата не в прошлом
                if date_obj.date() >= datetime.now().date():
                    return True
                else:
                    return False
            except ValueError:
                return False
    return False


def format_date_for_display(date_string: str) -> str:
    """Форматирует дату для отображения"""
    # Пробуем разные форматы
    patterns = [
        (r'^(\d{2})\.(\d{2})\.(\d{4})$', '{}.{}.{}'),
        (r'^(\d{2})-(\d{2})-(\d{4})$', '{}.{}.{}'),
        (r'^(\d{2})/(\d{2})/(\d{4})$', '{}.{}.{}'),
        (r'^(\d{4})-(\d{2})-(\d{2})$', '{}.{}.{}'),
    ]

    for pattern, output_format in patterns:
        match = re.match(pattern, date_string)
        if match:
            if pattern == r'^(\d{4})-(\d{2})-(\d{2})$':
                return output_format.format(match.group(3), match.group(2), match.group(1))
            else:
                return output_format.format(match.group(1), match.group(2), match.group(3))
    return date_string


@router.message(F.text == "📝 Оформить заказ")
async def start_order(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cart_items = db.get_cart(user_id)

    if not cart_items:
        await message.answer("❌ Корзина пуста! Добавьте товары в корзину.", reply_markup=kb.catalog)
        return

    await state.set_state(OrderStates.choosing_delivery)
    await message.answer("🚚 Выберите способ получения:", reply_markup=kb.order_menu)


@router.message(OrderStates.choosing_delivery, F.text.in_(["🚚 Доставка", "🏪 Самовывоз"]))
async def process_delivery(message: Message, state: FSMContext):
    delivery = "delivery" if message.text == "🚚 Доставка" else "pickup"
    await state.update_data(delivery_type=delivery)

    if delivery == "delivery":
        await state.set_state(OrderStates.entering_address)
        await message.answer(
            "📍 Введите адрес доставки (город, улица, дом, квартира):",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(address="Самовывоз: г. Москва, ул. Кондитерская, д. 10")
        await state.set_state(OrderStates.choosing_date)

        # Показываем примеры форматов даты
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")

        await message.answer(
            f"📅 Введите желаемую дату получения заказа\n\n"
            f"Примеры форматов:\n"
            f"• 31.12.2024\n"
            f"• 31-12-2024\n"
            f"• 31/12/2024\n"
            f"• 2024-12-31\n\n"
            f"📌 Минимальная дата: {tomorrow}\n"
            f"📌 Рекомендуемая дата: {tomorrow} или {day_after}\n\n"
            f"❗ Дата не может быть сегодня или в прошлом",
            reply_markup=kb.date_input_menu
        )


@router.message(OrderStates.entering_address, F.text)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.choosing_date)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    day_after = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")

    await message.answer(
        f"📅 Введите желаемую дату получения заказа\n\n"
        f"Примеры форматов:\n"
        f"• 31.12.2024\n"
        f"• 31-12-2024\n"
        f"• 31/12/2024\n"
        f"• 2024-12-31\n\n"
        f"📌 Минимальная дата: {tomorrow}\n"
        f"📌 Рекомендуемая дата: {tomorrow} или {day_after}\n\n"
        f"❗ Дата не может быть сегодня или в прошлом",
        reply_markup=kb.date_input_menu
    )


@router.message(OrderStates.choosing_date, F.text)
async def process_date(message: Message, state: FSMContext):
    date_text = message.text.strip()

    # Проверка на кнопки с датами
    if date_text == "📅 Завтра":
        date_obj = datetime.now() + timedelta(days=1)
        formatted_date = date_obj.strftime("%d.%m.%Y")
        await state.update_data(date=formatted_date)
        await state.set_state(OrderStates.entering_time)
        await message.answer(
            f"✅ Дата выбрана: {formatted_date}\n\n"
            f"⏰ Введите время (например: 15:00):",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    elif date_text == "📅 Послезавтра":
        date_obj = datetime.now() + timedelta(days=2)
        formatted_date = date_obj.strftime("%d.%m.%Y")
        await state.update_data(date=formatted_date)
        await state.set_state(OrderStates.entering_time)
        await message.answer(
            f"✅ Дата выбрана: {formatted_date}\n\n"
            f"⏰ Введите время (например: 15:00):",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Проверяем корректность введенной даты
    if not validate_date(date_text):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        await message.answer(
            f"❌ Неверный формат даты или дата в прошлом!\n\n"
            f"Пожалуйста, введите дату в одном из форматов:\n"
            f"• 31.12.2024\n"
            f"• 31-12-2024\n"
            f"• 31/12/2024\n"
            f"• 2024-12-31\n\n"
            f"📌 Дата не может быть сегодня или в прошлом\n"
            f"📌 Минимальная дата: {tomorrow}\n\n"
            f"Или используйте кнопки:",
            reply_markup=kb.date_input_menu
        )
        return

    # Сохраняем дату
    formatted_date = format_date_for_display(date_text)
    await state.update_data(date=formatted_date)

    await state.set_state(OrderStates.entering_time)
    await message.answer(
        f"✅ Дата выбрана: {formatted_date}\n\n"
        f"⏰ Введите время (например: 15:00):",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(OrderStates.entering_time, F.text)
async def process_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)

    data = await state.get_data()
    user_id = message.from_user.id
    cart_items = db.get_cart(user_id)
    cart_total = db.get_cart_total(user_id)

    # Формируем сообщение для подтверждения
    delivery_type_text = "Доставка" if data['delivery_type'] == 'delivery' else "Самовывоз"

    confirm = f"📦 ПРОВЕРЬТЕ ЗАКАЗ\n\n"
    confirm += f"🚚 Способ: {delivery_type_text}\n"
    confirm += f"📍 Адрес: {data['address']}\n"
    confirm += f"📅 Дата: {data['date']}\n"
    confirm += f"⏰ Время: {data['time']}\n\n"
    confirm += "🛍️ Состав:\n"

    for item in cart_items:
        total = item['price'] * item['quantity']
        confirm += f"• {item['name']} — {item['price']}₽ x {item['quantity']} = {total}₽\n"

    confirm += f"\n💰 ИТОГО: {cart_total}₽"

    await state.set_state(OrderStates.confirming)
    await message.answer(confirm, reply_markup=kb.confirm_order_menu)


@router.message(OrderStates.confirming, F.text == "✅ Подтвердить заказ")
async def confirm_order(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cart_items = db.get_cart(user_id)
    cart_total = db.get_cart_total(user_id)
    data = await state.get_data()

    # Сохраняем заказ в БД
    order_id = db.create_order(user_id, {
        "delivery_type": data['delivery_type'],
        "address": data['address'],
        "delivery_date": data['date'],
        "delivery_time": data['time'],
        "total_amount": cart_total,
        "comment": ""
    })

    # Получаем номер заказа
    order_details = db.get_order_details(order_id)
    order_number = order_details['order_number']

    # Формируем сообщение для кондитера
    delivery_type_text = "Доставка" if data['delivery_type'] == 'delivery' else "Самовывоз"

    order_text = f"🆕 НОВЫЙ ЗАКАЗ!\n\n"
    order_text += f"👤 Клиент: @{message.from_user.username or 'нет username'}\n"
    order_text += f"🆔 ID: {user_id}\n"
    order_text += f"📅 Время заказа: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    order_text += f"🔢 Номер заказа: {order_number}\n\n"
    order_text += f"🚚 Способ: {delivery_type_text}\n"
    order_text += f"📍 Адрес: {data['address']}\n"
    order_text += f"📅 Дата получения: {data['date']}\n"
    order_text += f"⏰ Время: {data['time']}\n\n"
    order_text += "🛍️ СОСТАВ ЗАКАЗА:\n"

    for item in cart_items:
        total = item['price'] * item['quantity']
        order_text += f"• {item['name']} — {item['price']}₽ x {item['quantity']} = {total}₽\n"

    order_text += f"\n💰 ИТОГО: {cart_total}₽"

    # Отправляем кондитеру
    try:
        logger.info(f"🔄 Отправка заказа #{order_number} админу {ADMIN_ID}...")
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=order_text
        )
        logger.info(f"✅ Заказ #{order_number} успешно отправлен!")

        # Подтверждение пользователю
        await message.answer(
            f"✅ ЗАКАЗ #{order_number} ПРИНЯТ!\n\n"
            f"Спасибо за заказ! Кондитер свяжется с вами в ближайшее время.\n"
            f"Номер заказа: {order_number}\n"
            f"Дата получения: {data['date']}\n"
            f"Время: {data['time']}",
            reply_markup=kb.main_menu
        )

    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        await message.answer(
            f"❌ Произошла ошибка при отправке заказа #{order_number}.\n"
            f"Пожалуйста, свяжитесь с кондитером напрямую: @confectioner\n"
            f"И сообщите номер заказа: {order_number}",
            reply_markup=kb.main_menu
        )

    # Очищаем корзину и состояние
    db.clear_cart(user_id)
    await state.clear()


@router.message(OrderStates.confirming, F.text == "❌ Отменить")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Заказ отменен", reply_markup=kb.catalog)


@router.message(F.text == "🔙 Назад в корзину")
async def back_to_cart(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    cart_items = db.get_cart(user_id)

    if not cart_items:
        await message.answer("🛍️ Корзина пуста", reply_markup=kb.catalog)
        return

    text = "🛍️ КОРЗИНА\n\n"
    for item in cart_items:
        total = item['price'] * item['quantity']
        text += f"• {item['name']} — {item['price']}₽ x {item['quantity']} = {total}₽\n"
    text += f"\n💰 ИТОГО: {db.get_cart_total(user_id)}₽"

    await message.answer(text, reply_markup=kb.cart_menu)


@router.message(F.text == "🔙 Назад")
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
    await back_to_cart(message, state)