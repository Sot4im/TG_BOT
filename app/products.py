from app.models import Product

# Каталог продуктов
PRODUCTS = {
    # Бенто-торты
    "bento_caramel_arahis": Product(
        id="bento_caramel_arahis",
        name="🍫 Карамель с арахисом",
        price=1500,
        category="bento",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, сливочной карамели с соленным арахисом и ганашом на темном шоколаде (можно сделать без арахиса)",
        weight="600г"
    ),
    "bento_berry": Product(
        id="bento_berry",
        name="🍓 Ягода-ваниль",
        price=1500,
        category="bento",
        description="Ванильный бисквит с прослойкой из кремчиза, ягодной начинки и ванильного ганаша",
        weight="600г"
    ),
    "bento_cherry": Product(
        id="bento_cherry",
        name="🍒 Вишня шоколад",
        price=1500,
        category="bento",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, вишневого конфитюра и ганаша на молочном шоколаде",
        weight="600г"
    ),
    "bento_banana": Product(
        id="bento_banana",
        name="🍌 Банан-карамель",
        price=1500,
        category="bento",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, сливочной карамели с бананами и ганашом на темном шоколаде с криспи",
        weight="600г"
    ),

    # Торты от 1 кг
    "cake_medovik": Product(
        id="cake_medovik",
        name="🍯 Медовик",
        price=1800,
        category="large_cake",
        description="Нежные медовые коржи со сметанным кремом",
        weight="от 1 кг"
    ),
    "cake_cherry": Product(
        id="cake_cherry",
        name="🍒 Вишня-шоколад",
        price=1900,
        category="large_cake",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, вишневого конфитюра и ганаша на молочном шоколаде",
        weight="от 1 кг"
    ),
    "cake_red_velvet": Product(
        id="cake_red_velvet",
        name="❤️ Красный бархат",
        price=2100,
        category="large_cake",
        description="Красные коржи с крем-чизом",
        weight="от 1.5 кг"
    ),
    "cake_caramel": Product(
        id="cake_caramel",
        name="🍫 Карамель с арахисом",
        price=2000,
        category="large_cake",
        description="Карамельный бисквит с орехами",
        weight="от 1.5 кг"
    ),
    "cake_berry": Product(
        id="cake_berry",
        name="🍓 Ягода-ваниль",
        price=2000,
        category="large_cake",
        description="Ванильный бисквит с ягодами",
        weight="от 1.5 кг"
    ),
    "cake_milk_girl": Product(
        id="cake_milk_girl",
        name="🥛 Молочная девочка",
        price=1900,
        category="large_cake",
        description="Нежные блинные коржи со сгущенкой",
        weight="от 1.5 кг"
    ),

# Меренговые рулеты
"meringue_berry": Product(
    id="meringue_berry",
    name="🍓 Ягодный меренговый рулет",
    price=450,
    category="meringue",
    description="Нежный меренговый рулет с ягодным кремом и свежими ягодами",
    weight="200г"
),
"meringue_chocolate": Product(
    id="meringue_chocolate",
    name="🍫 Шоколадный меренговый рулет",
    price=450,
    category="meringue",
    description="Воздушный меренговый рулет с шоколадным кремом и какао",
    weight="200г"
),
"meringue_caramel": Product(
    id="meringue_caramel",
    name="🍯 Карамельный меренговый рулет",
    price=480,
    category="meringue",
    description="Нежный меренговый рулет с соленой карамелью и орехами",
    weight="200г"
),
"meringue_pistachio": Product(
    id="meringue_pistachio",
    name="💚 Фисташковый меренговый рулет",
    price=520,
    category="meringue",
    description="Изысканный меренговый рулет с фисташковым кремом",
    weight="200г"
),
}

def get_product_by_id(product_id: str) -> Product:
    return PRODUCTS.get(product_id)

def get_products_by_category(category: str) -> list:
    return [p for p in PRODUCTS.values() if p.category == category]