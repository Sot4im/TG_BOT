import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import app.keyboards as kb
import app.texts as txt
from app.storage import get_cart, get_favorites
from app.products import get_product_by_id
from app.database import db

router = Router()
logger = logging.getLogger(__name__)

user_messages = {}


async def safe_delete(message: Message):
    try:
        await message.delete()
    except:
        pass


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id

    # Сохраняем пользователя в БД
    db.save_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await safe_delete(message)
    sent = await message.answer(
        txt.START_TEXT,
        reply_markup=kb.main_menu
    )
    user_messages[user_id] = sent


@router.message(F.text == "🛒 Каталог")
async def catalog_menu(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)

    if user_id in user_messages:
        try:
            await user_messages[user_id].edit_text(
                txt.CATALOG_TEXT,
                reply_markup=kb.catalog
            )
            return
        except:
            pass

    sent = await message.answer(txt.CATALOG_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🍰 Торты")
async def cakes_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.CAKES_TEXT, reply_markup=kb.cakes_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🍰 Бенто торты")
async def bento_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.BENTO_SECTION_TEXT, reply_markup=kb.bento_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🎂 Торты от 1кг")
async def large_cakes_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.LARGE_CAKES_TEXT, reply_markup=kb.choose_cake_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🍩 Штучные десерты")
async def boxed_desserts(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.BOXED_DESSERTS_TEXT, reply_markup=kb.boxed_desserts_menu)
    user_messages[user_id] = sent


@router.message(F.text == "⚪ Mochi")
async def mochi_menu_handler(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.MOCHI_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🍥 Macarons")
async def macarons_menu_handler(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.MACARONS_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🍩 Donut cake")
async def donut_cake_menu_handler(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.DONAT_CAKE_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


# Обработчик добавления бенто-тортов
@router.message(F.text.in_([
    "🍒 Вишня-шоколад (1200₽)", "🍓 Ягода-ваниль (1200₽)",
    "🍫 Шоколад-карамель (1300₽)", "🍌 Банан-карамель (1250₽)"
]))
async def add_bento_to_cart(message: Message):
    user_id = message.from_user.id

    product_map = {
        "🍒 Вишня-шоколад (1200₽)": "bento_cherry",
        "🍓 Ягода-ваниль (1200₽)": "bento_berry",
        "🍫 Шоколад-карамель (1300₽)": "bento_caramel",
        "🍌 Банан-карамель (1250₽)": "bento_banana"
    }

    product_id = product_map.get(message.text)
    if product_id:
        product = get_product_by_id(product_id)
        if product:
            db.add_to_cart(user_id, product.id)

            cart_count = db.get_cart_count(user_id)
            cart_total = db.get_cart_total(user_id)

            await message.answer(
                f"✅ {product.name} добавлен в корзину!\n"
                f"🛍️ В корзине: {cart_count} товаров на {cart_total}₽",
                reply_markup=kb.bento_menu
            )


# Обработчик добавления тортов от 1кг
@router.message(F.text.in_([
    "🍯 Медовик (1800₽/кг)", "🍒 Вишня-шоколад (1900₽/кг)",
    "❤️ Красный бархат (2100₽/кг)", "🍫 Карамель (2000₽/кг)",
    "🍓 Ягода-ваниль (2000₽/кг)", "🥛 Молочная девочка (1900₽/кг)"
]))
async def add_cake_to_cart(message: Message):
    user_id = message.from_user.id

    product_map = {
        "🍯 Медовик (1800₽/кг)": "cake_medovik",
        "🍒 Вишня-шоколад (1900₽/кг)": "cake_cherry",
        "❤️ Красный бархат (2100₽/кг)": "cake_red_velvet",
        "🍫 Карамель (2000₽/кг)": "cake_caramel",
        "🍓 Ягода-ваниль (2000₽/кг)": "cake_berry",
        "🥛 Молочная девочка (1900₽/кг)": "cake_milk_girl"
    }

    product_id = product_map.get(message.text)
    if product_id:
        product = get_product_by_id(product_id)
        if product:
            db.add_to_cart(user_id, product.id)

            cart_count = db.get_cart_count(user_id)
            cart_total = db.get_cart_total(user_id)

            await message.answer(
                f"✅ {product.name} добавлен в корзину!\n"
                f"🛍️ В корзине: {cart_count} товаров на {cart_total}₽",
                reply_markup=kb.choose_cake_menu
            )


@router.message(F.text == "🛍️ В корзину")
async def add_to_cart_prompt(message: Message):
    await message.answer(
        "Корзина",
        reply_markup=kb.cart_menu
    )
@router.message(F.text == "🛍️ Корзина")
async def show_cart(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)

    cart_items = db.get_cart(user_id)

    if not cart_items:
        sent = await message.answer("🛍️ Корзина пуста", reply_markup=kb.catalog)
        user_messages[user_id] = sent
        return

    text = "🛍️ *КОРЗИНА*\n\n"
    for item in cart_items:
        total = item['price'] * item['quantity']
        text += f"• {item['name']} — {item['price']}₽ x {item['quantity']} = {total}₽\n"
    text += f"\n💰 *ИТОГО: {db.get_cart_total(user_id)}₽*"

    sent = await message.answer(text, parse_mode="Markdown", reply_markup=kb.cart_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🗑️ Очистить корзину")
async def clear_cart(message: Message):
    user_id = message.from_user.id
    db.clear_cart(user_id)
    await message.answer("✅ Корзина очищена", reply_markup=kb.catalog)


@router.message(F.text == "🎀 Обо мне")
async def about(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.ABOUT_TEXT, parse_mode="Markdown", reply_markup=kb.main_menu)
    user_messages[user_id] = sent


@router.message(F.text == "👤 Контакты")
async def contacts(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.CONTACTS_TEXT, reply_markup=kb.main_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🔙 Назад в главное меню")
async def back_to_main(message: Message):
    user_id = message.from_user.id

    if user_id in user_messages:
        try:
            await user_messages[user_id].delete()
        except:
            pass

    sent = await message.answer("🏠 Главное меню:", reply_markup=kb.main_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🔙 Назад в каталог")
async def back_to_catalog(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.CATALOG_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "📦 Мои заказы")
async def show_my_orders(message: Message):
    user_id = message.from_user.id
    orders = db.get_user_orders(user_id)

    if not orders:
        await message.answer("📦 У вас пока нет заказов", reply_markup=kb.main_menu)
        return

    text = "📦 *МОИ ЗАКАЗЫ*\n\n"
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'completed': '✅',
            'cancelled': '❌'
        }.get(order['status'], '📋')

        text += f"{status_emoji} *Заказ #{order['order_number']}*\n"
        text += f"   Статус: {order['status']}\n"
        text += f"   Сумма: {order['total_amount']}₽\n"
        text += f"   Дата: {order['delivery_date']}\n"
        text += f"   Время: {order['delivery_time']}\n\n"

    await message.answer(text, parse_mode="Markdown", reply_markup=kb.main_menu)


@router.message()
async def handle_unknown(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)

    sent = await message.answer(
        "Пожалуйста, используйте кнопки меню.",
        reply_markup=kb.main_menu
    )
    user_messages[user_id] = sent