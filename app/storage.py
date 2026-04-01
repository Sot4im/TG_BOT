from typing import Dict
from app.models import Cart, Favorites

# Хранилище данных пользователей
user_carts: Dict[int, Cart] = {}
user_favorites: Dict[int, Favorites] = {}

def get_cart(user_id: int) -> Cart:
    """Получить корзину пользователя"""
    if user_id not in user_carts:
        user_carts[user_id] = Cart(user_id=user_id)
    return user_carts[user_id]

def get_favorites(user_id: int) -> Favorites:
    """Получить избранное пользователя"""
    if user_id not in user_favorites:
        user_favorites[user_id] = Favorites(user_id=user_id)
    return user_favorites[user_id]