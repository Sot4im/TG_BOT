from app.database import db
from app.products import get_product_by_id


class CartItem:
    """Элемент корзины для совместимости"""

    def __init__(self, product, quantity: int = 1, weight: float = 1.0):
        self.product = product
        self.quantity = quantity
        self.weight = weight

    @property
    def total_price(self) -> float:
        return self.product.price * self.quantity * self.weight


class Cart:
    """Корзина пользователя - адаптер для SQLite"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._items_cache = None

    def _load_items(self):
        """Загрузить товары из БД"""
        if self._items_cache is None:
            items_data = db.get_cart(self.user_id)
            self._items_cache = []
            for item in items_data:
                product = get_product_by_id(item['id'])
                if product:
                    self._items_cache.append(CartItem(product, item['quantity']))
        return self._items_cache

    @property
    def items(self):
        return self._load_items()

    @property
    def total(self) -> float:
        return db.get_cart_total(self.user_id)

    @property
    def is_empty(self) -> bool:
        return len(db.get_cart(self.user_id)) == 0

    def add_item(self, product, quantity: int = 1, weight: float = 1.0):
        db.add_to_cart(self.user_id, product.id, quantity)
        self._items_cache = None

    def remove_item(self, product_id: str):
        db.remove_from_cart(self.user_id, product_id)
        self._items_cache = None

    def clear(self):
        db.clear_cart(self.user_id)
        self._items_cache = None


class Favorites:
    """Избранное пользователя - адаптер для SQLite"""

    def __init__(self, user_id: int):
        self.user_id = user_id

    @property
    def product_ids(self):
        return db.get_favorites(self.user_id)

    def add(self, product_id: str):
        db.add_to_favorites(self.user_id, product_id)

    def remove(self, product_id: str):
        db.remove_from_favorites(self.user_id, product_id)


def get_cart(user_id: int) -> Cart:
    """Получить корзину пользователя"""
    return Cart(user_id)


def get_favorites(user_id: int) -> Favorites:
    """Получить избранное пользователя"""
    return Favorites(user_id)