from typing import Dict
from fastapi import APIRouter, Depends, FastAPI, Request
import os
import platform as plat
from functools import wraps
from hashlib import sha256
from pathlib import Path

from diskcache import Cache

from routes import userRoute

ROOT_DIR_PROJECT = Path(__file__).parent
if plat.system() == "Windows":
    path = str(ROOT_DIR_PROJECT) + os.sep + "cache_dir"
else:
    path = str(ROOT_DIR_PROJECT) + os.sep + "cache_dir"
cache = Cache(path)
cache_route = APIRouter(tags=["Cache"])


def cache_decorator(expire=10):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            serialized_args = dict(args)
            serialized_kwargs = dict(kwargs)
            print(serialized_kwargs.get('request').scope.get('path'))
            print(serialized_kwargs.get('request').__dict__)
            print(serialized_kwargs.get('request').headers)
            print(serialized_kwargs.get('request').headers.get('Authorization'))
            token = serialized_kwargs.get('request').headers.get(
                'Authorization').split('Bearer')[1].strip()
            current_user: dict = await userRoute.get_current_user(token)
            print(current_user)
            # Create a unique cache key based on function name and parameters
            # key = sha256(
            #     f"{func.__name__}{serialized_kwargs.get('req')}{serialized_kwargs.get('request').url.path}".encode(
            #     )
            # ).hexdigest()
            key = sha256(str((func.__name__, serialized_args,
                         serialized_kwargs)).encode()).hexdigest()
            key = sha256((func.__name__, args, kwargs).encode()).hexdigest()
            # print(key)
            data = cache.get(key)
            if not data:
                data = await func(*args, **kwargs)
                cache.set(key, data, expire=expire)
            return data

        return wrapper

    return decorator


@cache_route.get("/cache")
async def get_cache(request: Request, current_user: dict = Depends(userRoute.get_current_user)) -> Dict:
    """
    API to fetch all data currently stored in the cache.
    Returns a dictionary of cached keys and their values.
    """
    data = {}
    for key in cache:
        data[key] = cache.get(key)
    return {"cache": data}


@ cache_route.post("/cache")
async def add_to_cache(request: Request, key: str, value: str, expire: int = 3600, current_user: dict = Depends(userRoute.get_current_user)):
    """
    API to add a key-value pair to the cache.
    """
    cache.set(key, value, expire=expire)
    return {"message": f"Key '{key}' added to cache with expiration {expire} seconds."}


@ cache_route.delete("/cache/{key}")
async def delete_from_cache(key: str, request: Request, current_user: dict = Depends(userRoute.get_current_user)):
    """
    API to delete a specific key from the cache.
    """
    if key in cache:
        cache.delete(key)
        return {"message": f"Key '{key}' removed from cache."}
    return {"error": f"Key '{key}' not found in cache."}


@ cache_route.delete("/cache")
async def clear_cache(request: Request, current_user: dict = Depends(userRoute.get_current_user)):
    """
    API to clear the entire cache.
    """
    cache.clear()
    return {"message": "All cache cleared successfully."}
