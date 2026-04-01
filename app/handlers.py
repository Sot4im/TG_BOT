import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import app.keyboards as kb
import app.texts as txt
from app.storage import get_cart, get_favorites
from app.products import get_product_by_id

router = Router()
logger = logging.getLogger(__name__)

# Хранилище для временных данных выбора веса
temp_weight_selection = {}

user_messages = {}


async def safe_delete(message: Message):
    try:
        await message.delete()
    except:
        pass


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
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



@router.message(F.text == "🍩 Штучные десерты")
async def desserts_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.BOXED_DESSERTS_TEXT, reply_markup=kb.boxed_desserts_menu)
    user_messages[user_id] = sent


@router.message(F.text == "⚪ Mochi")
async def desserts_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.MOCHI_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🍥 Macarons")
async def desserts_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.MACARONS_TEXT, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🍩 Donut cake")
async def desserts_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.DONAT_CAKE, reply_markup=kb.catalog)
    user_messages[user_id] = sent




# Обработчик для кнопки "🍥 Меренговые рулеты" в каталоге
@router.message(F.text == "🍥 Меренговые рулеты")
async def meringue_section(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(
        "🍥 *Меренговые рулеты*\n\n"
        "Нежные, воздушные рулеты из меренги.\n"
        "Вес: 200г\n\n"
        "Выберите вкус:",
        parse_mode="Markdown",
        reply_markup=kb.meringue_menu
    )
    user_messages[user_id] = sent

# Обработчик добавления меренговых рулетов в корзину
@router.message(F.text.in_([
    "🍓 Ягодный рулет (450₽)", "🍫 Шоколадный рулет (450₽)",
    "🍯 Карамельный рулет (480₽)", "💚 Фисташковый рулет (520₽)"
]))
async def add_meringue_to_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)

    product_map = {
        "🍓 Ягодный рулет (450₽)": "meringue_berry",
        "🍫 Шоколадный рулет (450₽)": "meringue_chocolate",
        "🍯 Карамельный рулет (480₽)": "meringue_caramel",
        "💚 Фисташковый рулет (520₽)": "meringue_pistachio"
    }

    product_id = product_map.get(message.text)
    if product_id:
        product = get_product_by_id(product_id)
        cart.add_item(product)

        await message.answer(
            f"✅ {product.name} добавлен в корзину!\n"
            f"🛍️ В корзине: {len(cart.items)} товаров на {cart.total}₽",
            reply_markup=kb.meringue_menu
        )

    sent = await message.answer(
      reply_markup=kb.back_to_catalog_only
    )
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


# Обработка выбора торта от 1 кг
@router.message(F.text.in_([
    "🍯 Медовик (1800₽/кг)", "🍒 Вишня-шоколад (1900₽/кг)",
    "❤️ Красный бархат (2100₽/кг)", "🍫 Карамель (2000₽/кг)",
    "🍓 Ягода-ваниль (2000₽/кг)", "🥛 Молочная девочка (1900₽/кг)"
]))
async def select_cake_weight(message: Message):
    user_id = message.from_user.id

    # Маппинг названий к ID продуктов
    product_map = {
        "🍯 Медовик (1800₽/кг)": "cake_medovik",
        "🍒 Вишня-шоколад (1900₽/кг)": "cake_cherry",
        "❤️ Красный бархат (2100₽/кг)": "cake_red_velvet",
        "🍫 Карамель (2000₽/кг)": "cake_caramel",
        "🍓 Ягода-ваниль (2000₽/кг)": "cake_berry",
        "🥛 Молочная девочка (1900₽/кг)": "cake_milk_girl"
    }

    product_id = product_map.get(message.text)
    temp_weight_selection[user_id] = product_id

    await safe_delete(message)
    sent = await message.answer(
        f"⚖️ Выберите вес торта:\n\n"
        f"Цена указана за 1 кг. Итоговая стоимость = вес × цена за кг\n\n"
        f"Доступные веса: 1кг, 1.5кг, 2кг, 2.5кг, 3кг",
        reply_markup=kb.weight_menu
    )
    user_messages[user_id] = sent


# Обработка выбора веса
@router.message(F.text.startswith("⚖️ "))
async def process_weight_selection(message: Message):
    user_id = message.from_user.id

    if user_id not in temp_weight_selection:
        await message.answer("Пожалуйста, сначала выберите торт", reply_markup=kb.choose_cake_menu)
        return

    # Извлекаем вес из текста кнопки
    weight_text = message.text.replace("⚖️ ", "").replace(" кг", "")
    try:
        weight = float(weight_text)
    except:
        await message.answer("❌ Неверный формат веса", reply_markup=kb.choose_cake_menu)
        return

    product_id = temp_weight_selection[user_id]
    product = get_product_by_id(product_id)

    if not product:
        await message.answer("❌ Товар не найден", reply_markup=kb.choose_cake_menu)
        return

    cart = get_cart(user_id)
    total_price = product.price * weight

    cart.add_item(product, weight_kg=weight)

    # Очищаем временные данные
    del temp_weight_selection[user_id]

    await safe_delete(message)

    # Формируем ответ
    response = (
        f"✅ {product.name} ({weight}кг) добавлен в корзину!\n\n"
        f"📊 Стоимость: {product.price}₽/кг × {weight}кг = {total_price}₽\n"
        f"🛍️ В корзине: {len(cart.items)} товаров на {cart.total}₽"
    )

    sent = await message.answer(response, reply_markup=kb.choose_cake_menu)
    user_messages[user_id] = sent


@router.message(F.text.in_([
    "🍒 Вишня-шоколад (1500₽)", "🍓 Ягода-ваниль (1500₽)",
    "🍫 Карамель с арахисом (1500₽)", "🍌 Банан-карамель (1500₽)"
]))
async def add_bento_to_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)

    product_map = {
        "🍒 Вишня-шоколад (1500₽)": "bento_cherry",
        "🍓 Ягода-ваниль (1500₽)": "bento_berry",
        "🍫 Карамель с арахисом (1500₽)": "bento_caramel_arahis",
        "🍌 Банан-карамель (1500₽)": "bento_banana"
    }

    product_id = product_map.get(message.text)
    if product_id:
        product = get_product_by_id(product_id)
        cart.add_item(product)

        await message.answer(
            f"✅ {product.name} добавлен в корзину!\n"
            f"🛍️ В корзине: {len(cart.items)} товаров на {cart.total}₽",
            reply_markup=kb.bento_menu
        )





@router.message(F.text == "🛍️ В корзину")
async def add_to_cart_prompt(message: Message):
    await message.answer(
        "Выберите товар из меню, чтобы добавить его в корзину",
        reply_markup=kb.catalog
    )


@router.message(F.text == "❤️ Избранное")
async def show_favorites(message: Message):
    user_id = message.from_user.id
    favorites = get_favorites(user_id)
    await safe_delete(message)

    if not favorites.product_ids:
        sent = await message.answer(
            "❤️ В избранном пока пусто",
            reply_markup=kb.catalog
        )
        user_messages[user_id] = sent
        return

    text = "❤️ ИЗБРАННОЕ\n\n"
    for pid in favorites.product_ids:
        product = get_product_by_id(pid)
        if product:
            text += f"• {product.name} — {product.price}₽\n"

    sent = await message.answer(text, reply_markup=kb.catalog)
    user_messages[user_id] = sent


@router.message(F.text == "🛍️ Корзина")
async def show_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)
    await safe_delete(message)

    if cart.is_empty:
        sent = await message.answer("🛍️ Корзина пуста", reply_markup=kb.catalog)
        user_messages[user_id] = sent
        return

    text = "🛍️ КОРЗИНА\n\n"
    for item in cart.items:
        if item.weight_kg:
            text += f"• {item.display_name} — {item.total_price}₽ ({item.product.price}₽/кг)\n"
        else:
            text += f"• {item.display_name} — {item.total_price}₽\n"
    text += f"\n💰 ИТОГО: {cart.total}₽"

    sent = await message.answer(text, reply_markup=kb.cart_menu)
    user_messages[user_id] = sent


@router.message(F.text == "🗑️ Очистить корзину")
async def clear_cart(message: Message):
    user_id = message.from_user.id
    cart = get_cart(user_id)
    cart.clear()
    await message.answer("🗑️ Корзина очищена", reply_markup=kb.catalog)


@router.message(F.text == "🎀 Обо мне")
async def about(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.ABOUT_TEXT, reply_markup=kb.main_menu)
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
    await safe_delete(message)

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


@router.message(F.text == "🔙 Назад в меню тортов")
async def back_to_cakes_menu(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)
    sent = await message.answer(txt.LARGE_CAKES_TEXT, reply_markup=kb.choose_cake_menu)
    user_messages[user_id] = sent


@router.message()
async def handle_unknown(message: Message):
    user_id = message.from_user.id
    await safe_delete(message)

    sent = await message.answer(
        "Пожалуйста, используйте кнопки меню.",
        reply_markup=kb.main_menu
    )
    user_messages[user_id] = sent