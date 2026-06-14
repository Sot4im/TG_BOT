from app.models import Product

# Каталог продуктов
PRODUCTS = {
    # Бенто-торты
    "bento_caramel": Product(
        id="bento_caramel",
        name="🍫 Шоколад-карамель",
        price=1300,
        category="bento",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, сливочной карамели с соленным арахисом и ганашом на темном шоколаде (можно сделать без арахиса)",
        weight="600г"
    ),
    "bento_berry": Product(
        id="bento_berry",
        name="🍓 Ягода-ваниль",
        price=1200,
        category="bento",
        description="Ванильный бисквит с прослойкой из кремчиза, ягодной начинки и ванильного ганаша",
        weight="600г"
    ),
    "bento_cherry": Product(
        id="bento_cherry",
        name="🍒 Вишня-шоколад",
        price=1200,
        category="bento",
        description="Насыщенный шоколадный бисквит с прослойкой из кремчиза, вишневого конфитюра и ганаша на молочном шоколаде",
        weight="600г"
    ),
    "bento_banana": Product(
        id="bento_banana",
        name="🍌 Банан-карамель",
        price=1250,
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
        name="🍫 Карамель",
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
}


def get_product_by_id(product_id: str) -> Product:
    return PRODUCTS.get(product_id)


def get_products_by_category(category: str) -> list:
    return [p for p in PRODUCTS.values() if p.category == category]