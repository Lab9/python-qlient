import json
import os
import tempfile
import time
import uuid
from abc import ABC, abstractmethod
from os import path
from typing import Union, Dict, List, Callable, Optional

CacheValueType = Union[str, int, float, Dict, List]
CACHE_VALUE_INSTANCE_TYPE_TUPLE = (str, int, float, Dict, List)


def as_uuid(key: str) -> str:
    """ Turn the given key into a uuid version 3. """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, key))


class CachedValue:
    """
    The CachedValue class represents the object that is being stored within the cache.
    This makes it easier for me to check the ttl and optionally reinitialize the value.
    """

    def __init__(self, key: str, value: CacheValueType, init_time: float):
        """
        Initialize a new cached value.

        :param key: holds the key assigned to the value
        :param value: holds the value to cache
        :param init_time: holds the initial  time
        """
        self.key = key
        self.value = value
        self.init_time = init_time


class Cache(ABC):
    """
    Abstract base class for a Cache object.
    Defines the necessary functions store and retrieve as well as is_expired,
    to ensure they are all equal and callable on each cache object.
    """

    def __init__(self, ttl: float = 30.0, timer: Callable = None):
        """
        Instantiate a new cache class.

        :param ttl: holds the time-to-live value of the cached object in seconds. Defaults to 30 seconds.
        :param timer: holds the timing function.
        """
        self.ttl = ttl
        self.timer = timer or time.monotonic

    @abstractmethod
    def store(self, endpoint: str, key: str, value: CacheValueType):
        """
        Method used to store a key value pair.
        """
        pass

    @abstractmethod
    def retrieve(self, endpoint: str, key: str) -> Optional[CacheValueType]:
        """
        Method used to retrieve a value from the cache.
        """
        pass

    def is_expired(self, value: CachedValue) -> bool:
        """ Method to evaluate a cached value whether it is expired or not. """
        return (self.timer() - value.init_time) > self.ttl


class MemoryCache(Cache):
    """
    Simple in memory cache implementation.
    This cache stores all values within a dictionary.
    """

    def __init__(self, **kwargs):
        """ Initialize a new in memory cache object """
        super(MemoryCache, self).__init__(**kwargs)
        self.mem_cache: Dict[str, Dict[str, CachedValue]] = {}

    def store(self, endpoint: str, key: str, value: CacheValueType):
        """
        This method stores a value into the dictionary cache by turning the endpoint and key into
        a uuid version 3 and assigning the value.

        :param endpoint: holds the client endpoint
        :param key: holds the value key
        :param value: holds the value itself
        """
        if not isinstance(value, CACHE_VALUE_INSTANCE_TYPE_TUPLE):
            raise ValueError(f"Required type str, int, float, dict, list. Found '{type(value)}'")
        endpoint_uuid = as_uuid(endpoint)
        if endpoint_uuid not in self.mem_cache:
            self.mem_cache[endpoint_uuid] = {}

        key_uuid = as_uuid(key)
        self.mem_cache[endpoint_uuid][key_uuid] = CachedValue(key, value, self.timer())

    def retrieve(self, endpoint: str, key: str) -> Optional[CacheValueType]:
        """
        This method retrieves a value from the dictionary cache by turning the endpoint and key into
        a uuid version 3 and checking for the value.
        If the value is not in the cache or if the value is expired, this method will return None.
        Otherwise the stored value.

        :param endpoint: holds the client endpoint
        :param key: holds the value key
        """
        endpoint_uuid = as_uuid(endpoint)
        if endpoint_uuid not in self.mem_cache:
            return None

        key_uuid = as_uuid(key)
        cached_obj: CachedValue = self.mem_cache[endpoint_uuid].get(key_uuid)
        if cached_obj is None:
            return None

        if self.is_expired(cached_obj):
            del self.mem_cache[endpoint_uuid][key_uuid]
            return None
        else:
            return cached_obj.value


class DiskCache(Cache):
    """ The DiskCache writes objects onto the disk. """

    def __init__(self, root=None, **kwargs):
        """
        Initialize a new DiskCache instance.

        :param root: holds an optional root folder.
        """
        super(DiskCache, self).__init__(**kwargs)
        self.root = root or path.join(tempfile.gettempdir(), "python-qlient")

    def get_file_path(self, endpoint: str, key: str) -> str:
        """
        This method returns the filepath to a cached object.
        It encodes the endpoint and key into a uuid version 3 which ultimately becomes the
        path to the cached object.
        The data is stored in a json like object.

        :param endpoint: holds the endpoint
        :param key: holds the cache key
        """
        endpoint_uuid = as_uuid(endpoint)
        key_uuid = as_uuid(key)
        file_name = f"{key_uuid}.json"
        folder_path = path.join(self.root, endpoint_uuid)
        if not path.exists(folder_path):
            os.makedirs(folder_path)
        return path.join(folder_path, file_name)

    def store(self, endpoint: str, key: str, value: CacheValueType):
        """
        Write an item onto the local disk.

        :param endpoint: holds the client endpoint
        :param key: holds the key assigned with the value
        :param value: holds the value to be stored.
        """
        if not isinstance(value, CACHE_VALUE_INSTANCE_TYPE_TUPLE):
            raise ValueError(f"Required type str, int, float, dict, list. Found '{type(value)}'")
        file_path = self.get_file_path(endpoint, key)
        cached_value = CachedValue(key, value, self.timer())
        data_to_store = {"key": cached_value.key, "value": cached_value.value, "init_time": cached_value.init_time}
        with open(file_path, "w", encoding="UTF-8") as json_file:
            json.dump(data_to_store, json_file, ensure_ascii=False)

    def retrieve(self, endpoint: str, key: str) -> Optional[CacheValueType]:
        """
        Read a cached object from the local disk.

        :param endpoint: holds the client endpoint
        :param key: holds the key assigned with the value
        """
        file_path = self.get_file_path(endpoint, key)
        if not path.exists(file_path):
            return None

        with open(file_path, "r", encoding="UTF-8") as json_file:
            stored_data = json.load(json_file)

        cached_value = CachedValue(stored_data["key"], stored_data["value"], stored_data["init_time"])
        if self.is_expired(cached_value):
            return None
        else:
            return cached_value.value
