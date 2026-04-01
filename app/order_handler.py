# app/order_handler.py
import logging
import re
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
import app.keyboards as kb
from app.storage import get_cart
from config import ADMIN_ID

router = Router()
logger = logging.getLogger(__name__)


class OrderStates(StatesGroup):
    choosing_delivery = State()
    entering_address = State()
    choosing_date = State()
    entering_time = State()
    confirming = State()


def validate_date(date_text: str) -> bool:
    """Проверка корректности даты"""
    # Проверяем формат ДД.ММ.ГГГГ
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, date_text):
        return False

    try:

        day, month, year = map(int, date_text.split('.'))
        input_date = datetime(year, month, day)

        # Проверяем, что дата не в прошлом
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if input_date < today:
            return False

        # Проверяем, что дата не слишком далеко (максимум 30 дней)
        max_date = today + timedelta(days=30)
        if input_date > max_date:
            return False

        return True
    except:
        return False


def validate_time(time_text: str) -> bool:
    """Проверка корректности времени"""
    pattern = r'^\d{2}:\d{2}$'
    if not re.match(pattern, time_text):
        return False

    try:
        hour, minute = map(int, time_text.split(':'))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True
        return False
    except:
        return False


@router.message(F.text == "📝 Оформить заказ")
async def start_order(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cart = get_cart(user_id)

    if cart.is_empty:
        await message.answer("❌ Корзина пуста! Добавьте товары в корзину.", reply_markup=kb.catalog)
        return

    await state.set_state(OrderStates.choosing_delivery)
    await message.answer(
        "🚚 Выберите способ получения:",
        reply_markup=kb.order_menu
    )


@router.message(OrderStates.choosing_delivery, F.text.in_(["🚚 Доставка", "🏪 Самовывоз"]))
async def process_delivery(message: Message, state: FSMContext):
    delivery = "delivery" if message.text == "🚚 Доставка" else "pickup"
    await state.update_data(delivery_type=delivery)

    if delivery == "delivery":
        await state.set_state(OrderStates.entering_address)
        await message.answer(
            "📍 Введите адрес доставки (город, улица, дом, квартира):\n\n"
            "Пример: г. Москва, ул. Ленина, д. 10, кв. 5",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await state.update_data(address="Самовывоз: г. Москва, ул. Кондитерская, д. 10")
        await state.set_state(OrderStates.choosing_date)
        await message.answer(
            "📅 Укажите дату самовывоза:\n\n"
            "Введите дату в формате ДД.ММ.ГГГГ\n"
            "Например: 15.05.2026\n\n"
            "⚠️ Заказы принимаются минимум за 2 дня до даты получения",
            reply_markup=kb.date_menu
        )


@router.message(OrderStates.entering_address, F.text)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.choosing_date)
    await message.answer(
        "📅 Укажите желаемую дату получения:\n\n"
        "Введите дату в формате ДД.ММ.ГГГГ\n"
        "Например: 15.05.2026\n\n"
        "⚠️ Минимальный срок изготовления - 2 дня\n"
        "⚠️ Заказы принимаются на даты не позднее 30 дней",
        reply_markup=kb.date_menu
    )


@router.message(OrderStates.choosing_date, F.text == "📅 Ввести дату вручную")
async def prompt_manual_date(message: Message, state: FSMContext):
    await message.answer(
        "📅 Введите дату в формате ДД.ММ.ГГГГ\n\n"
        "Примеры:\n"
        "• 15.05.2026 - 15 мая 2026 года\n"
        "• 20.12.2026 - 20 декабря 2026 года\n\n"
        "⚠️ Важно:\n"
        "• Дата должна быть не раньше, чем через 2 дня\n"
        "• Дата не должна быть позже, чем через 30 дней\n"
        "• Используйте точки для разделения",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(OrderStates.choosing_date, F.text == "🔙 Назад в корзину")
async def back_to_cart_from_date(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    cart = get_cart(user_id)

    if cart.is_empty:
        await message.answer("🛍️ Корзина пуста", reply_markup=kb.catalog)
        return

    text = "🛍️ КОРЗИНА\n\n"
    for item in cart.items:
        if item.weight_kg:
            text += f"• {item.display_name} — {item.total_price}₽ ({item.product.price}₽/кг)\n"
        else:
            text += f"• {item.display_name} — {item.total_price}₽\n"
    text += f"\n💰 ИТОГО: {cart.total}₽"

    await message.answer(text, reply_markup=kb.cart_menu)


@router.message(OrderStates.choosing_date, F.text)
async def process_date(message: Message, state: FSMContext):
    date_text = message.text.strip()

    # Проверяем корректность даты
    if not validate_date(date_text):
        await message.answer(
            "❌ Неверный формат даты!\n\n"
            "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n"
            "Например: 15.05.2026\n\n"
            "Важно:\n"
            "• Дата должна быть не раньше, чем через 2 дня\n"
            "• Дата не должна быть позже, чем через 30 дней\n"
            "• Используйте точки для разделения",
            reply_markup=kb.date_menu
        )
        return

    # Проверяем, что дата не раньше чем через 2 дня
    try:
        day, month, year = map(int, date_text.split('.'))
        input_date = datetime(year, month, day)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        min_date = today + timedelta(days=2)

        if input_date < min_date:
            await message.answer(
                f"❌ Минимальный срок изготовления - 2 дня!\n\n"
                f"Вы выбрали: {date_text}\n"
                f"Минимальная дата: {min_date.strftime('%d.%m.%Y')}\n\n"
                f"Пожалуйста, выберите другую дату:",
                reply_markup=kb.date_menu
            )
            return

        # Сохраняем дату
        await state.update_data(date=date_text)
        await state.set_state(OrderStates.entering_time)
        await message.answer(
            "⏰ Введите желаемое время получения:\n\n"
            "Введите время в формате ЧЧ:ММ\n"
            "Например: 15:00 или 18:30\n\n"
            "🕐 Режим работы: с 10:00 до 20:00",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        logger.error(f"Ошибка обработки даты: {e}")
        await message.answer(
            "❌ Ошибка при обработке даты.\n"
            "Пожалуйста, попробуйте еще раз в формате ДД.ММ.ГГГГ",
            reply_markup=kb.date_menu
        )


@router.message(OrderStates.entering_time, F.text)
async def process_time(message: Message, state: FSMContext):
    time_text = message.text.strip()

    # Проверяем корректность времени
    if not validate_time(time_text):
        await message.answer(
            "❌ Неверный формат времени!\n\n"
            "Пожалуйста, введите время в формате ЧЧ:ММ\n"
            "Например: 15:00 или 18:30\n\n"
            "Часы: от 00 до 23\n"
            "Минуты: от 00 до 59"
        )
        return

    # Проверяем, что время в рабочем диапазоне
    try:
        hour, minute = map(int, time_text.split(':'))
        if hour < 10 or hour > 20:
            await message.answer(
                "❌ Время вне рабочего диапазона!\n\n"
                "🕐 Режим работы: с 10:00 до 20:00\n\n"
                "Пожалуйста, выберите время в этом диапазоне:"
            )
            return
    except:
        pass

    await state.update_data(time=time_text)

    data = await state.get_data()
    user_id = message.from_user.id
    cart = get_cart(user_id)

    # Формируем сообщение для подтверждения
    confirm = "📦 ПРОВЕРЬТЕ ЗАКАЗ\n\n"
    confirm += f"🚚 Способ: {'Доставка' if data['delivery_type'] == 'delivery' else 'Самовывоз'}\n"
    confirm += f"📍 Адрес: {data['address']}\n"
    confirm += f"📅 Дата получения: {data['date']}\n"
    confirm += f"⏰ Время: {data['time']}\n\n"
    confirm += "🛍️ Состав:\n"

    for item in cart.items:
        if item.weight_kg:
            confirm += f"• {item.display_name} — {item.total_price}₽ ({item.product.price}₽/кг)\n"
        else:
            confirm += f"• {item.display_name} — {item.total_price}₽\n"

    confirm += f"\n💰 ИТОГО: {cart.total}₽"

    await state.set_state(OrderStates.confirming)
    await message.answer(confirm, reply_markup=kb.confirm_order_menu)


@router.message(OrderStates.confirming, F.text == "✅ Подтвердить заказ")
async def confirm_order(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cart = get_cart(user_id)
    data = await state.get_data()

    # Формируем сообщение для кондитера
    order_text = "🆕 НОВЫЙ ЗАКАЗ!\n\n"
    order_text += f"👤 Клиент: @{message.from_user.username or 'нет username'}\n"
    order_text += f"🆔 ID: {user_id}\n"
    order_text += f"📅 Время заказа: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    order_text += f"🚚 Способ: {'Доставка' if data['delivery_type'] == 'delivery' else 'Самовывоз'}\n"
    order_text += f"📍 Адрес: {data['address']}\n"
    order_text += f"📅 Дата получения: {data['date']}\n"
    order_text += f"⏰ Время: {data['time']}\n\n"
    order_text += "🛍️ СОСТАВ ЗАКАЗА:\n"

    for item in cart.items:
        if item.weight_kg:
            order_text += f"• {item.display_name} — {item.weight_kg}кг = {item.total_price}₽\n"
        else:
            order_text += f"• {item.display_name} — {item.total_price}₽\n"

    order_text += f"\n💰 ИТОГО: {cart.total}₽"

    # Отправляем кондитеру
    try:
        logger.info(f"🔄 Отправка заказа админу {ADMIN_ID}...")
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=order_text
        )
        logger.info(f"✅ Заказ успешно отправлен!")

        # Подтверждение пользователю
        await message.answer(
            f"✅ ЗАКАЗ ПРИНЯТ!\n\n"
            f"📅 Дата получения: {data['date']}\n"
            f"⏰ Время: {data['time']}\n"
            f"💰 Сумма: {cart.total}₽\n\n"
            f"Спасибо за заказ! Кондитер свяжется с вами в ближайшее время.\n"
            f"По всем вопросам: @CBM_KZN",
            reply_markup=kb.main_menu
        )

    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")

        # Пробуем отправить упрощенную версию
        try:
            simple_text = f"Новый заказ от пользователя {user_id} на сумму {cart.total}₽"
            await message.bot.send_message(ADMIN_ID, simple_text)
            logger.info("✅ Упрощенная версия отправлена")
        except:
            logger.error("❌ Не удалось отправить даже упрощенную версию")

        await message.answer(
            "❌ Произошла ошибка при отправке заказа.\n"
            "Пожалуйста, свяжитесь с кондитером напрямую: @confectioner",
            reply_markup=kb.main_menu
        )

    # Очищаем корзину и состояние
    cart.clear()
    await state.clear()


@router.message(OrderStates.confirming, F.text == "❌ Отменить")
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Заказ отменен", reply_markup=kb.catalog)


@router.message(F.text == "🔙 Назад в корзину")
async def back_to_cart(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    cart = get_cart(user_id)

    if cart.is_empty:
        await message.answer("🛍️ Корзина пуста", reply_markup=kb.catalog)
        return

    text = "🛍️ КОРЗИНА\n\n"
    for item in cart.items:
        if item.weight_kg:
            text += f"• {item.display_name} — {item.total_price}₽ ({item.product.price}₽/кг)\n"
        else:
            text += f"• {item.display_name} — {item.total_price}₽\n"
    text += f"\n💰 ИТОГО: {cart.total}₽"

    await message.answer(text, reply_markup=kb.cart_menu)


@router.message(F.text == "🔙 Назад")
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
    await back_to_cart(message, state)