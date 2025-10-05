import asyncio
from collections import OrderedDict
from functools import wraps
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict


@dataclass
class LRUCache:
    capacity: int
    cache: OrderedDict = field(default_factory=OrderedDict)

    def get(self, key: Any) -> Any:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict LRU

    def __contains__(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cache)


def cached(cache: LRUCache):
    """Decorator for caching function results in the given LRUCache."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                return cache.get(key)
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
        return wrapper
    return decorator


def async_cached(cache: LRUCache):
    """Decorator for caching async function results."""

    def decorator(func: Callable[..., Coroutine]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key in cache:
                return cache.get(key)
            result = await func(*args, **kwargs)
            cache.put(key, result)
            return result
        return wrapper
    return decorator


# ---------------- Example Usage ---------------- #
cache = LRUCache(capacity=3)


@cached(cache)
def heavy_computation(x: int) -> int:
    print(f"Computing {x}...")
    return x * x


@async_cached(cache)
async def async_heavy_computation(x: int) -> int:
    print(f"Async computing {x}...")
    await asyncio.sleep(1)  # simulate IO
    return x * x


if __name__ == "__main__":
    print(heavy_computation(10))  # computed
    print(heavy_computation(10))  # cached

    async def main():
        print(await async_heavy_computation(5))   # computed
        print(await async_heavy_computation(5))   # cached
        print(await async_heavy_computation(6))   # computed
        print(await async_heavy_computation(7))   # computed
        print(await async_heavy_computation(5))   # evicted earlier, recomputed

    asyncio.run(main())
