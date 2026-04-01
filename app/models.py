from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Product:
    """Модель товара"""
    id: str
    name: str
    price: float
    category: str
    description: str = ""
    weight: str = ""


@dataclass
class CartItem:
    """Элемент корзины"""
    product: Product
    quantity: int = 1
    weight_kg: Optional[float] = None

    @property
    def total_price(self) -> float:
        if self.weight_kg:
            return self.product.price * self.weight_kg
        return self.product.price * self.quantity

    @property
    def display_name(self) -> str:
        if self.weight_kg:
            return f"{self.product.name} ({self.weight_kg}кг)"
        return self.product.name


@dataclass
class Cart:
    """Корзина пользователя"""
    user_id: int
    items: List[CartItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, product: Product, quantity: int = 1, weight_kg: float = None):
        for item in self.items:
            if item.product.id == product.id and item.weight_kg == weight_kg:
                if weight_kg:
                    item.weight_kg = weight_kg
                else:
                    item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity, weight_kg))

    def remove_item(self, product_id: str, weight_kg: float = None):
        self.items = [item for item in self.items
                      if not (item.product.id == product_id and item.weight_kg == weight_kg)]

    def clear(self):
        self.items.clear()

    @property
    def total(self) -> float:
        return sum(item.total_price for item in self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0


@dataclass
class Favorites:
    """Избранное пользователя"""
    user_id: int
    product_ids: List[str] = field(default_factory=list)

    def add(self, product_id: str):
        if product_id not in self.product_ids:
            self.product_ids.append(product_id)

    def remove(self, product_id: str):
        if product_id in self.product_ids:
            self.product_ids.remove(product_id)