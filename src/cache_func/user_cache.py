import redis.asyncio as redis
import json
from src.databases.models import User

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


async def get_user_from_cache(email: str):
    """
    Отримати дані користувача з кешу Redis за email.
    """
    user_data = await r.get(email)
    if user_data:
        return json.loads(user_data)
    return None


async def set_user_to_cache(user: User):
    """
    Зберегти користувача в кеш Redis.
    """
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
        "role": user.role,
    }
    await r.set(user.email, json.dumps(user_dict), ex=3600)
