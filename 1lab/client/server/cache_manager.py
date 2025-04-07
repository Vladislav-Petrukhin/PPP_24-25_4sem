import hashlib
import time

class CacheManager:
    """
    Простая реализация кэша: словарь query_hash -> (timestamp, result).
    Можно расширять до продвинутых методов (LRU, ограничение по памяти и т.д.).
    """
    def __init__(self, ttl=60):
        self.ttl = ttl
        self.cache = {}  # {hash: (time, result)}

    def get_from_cache(self, query_info: dict):
        # Формируем ключ (хэш) на основе query_info
        key = self._make_key(query_info)
        if key in self.cache:
            timestamp, result = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                # устарело
                del self.cache[key]
        return None

    def save_to_cache(self, query_info: dict, result: str):
        key = self._make_key(query_info)
        self.cache[key] = (time.time(), result)

    def _make_key(self, query_info: dict) -> str:
        # Сериализуем dict в строку и берём хэш
        raw_str = str(query_info)
        return hashlib.md5(raw_str.encode("utf-8")).hexdigest()
