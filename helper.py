# -*- coding: utf-8 -*-

from config import constants
from werkzeug.contrib.cache import MemcachedCache
import redis


class CacheInit:
    """
    Class for initializing memcache and Redis connections interfaces.
    Constants are kept in a separate file from flask settings
    """
    def __init__(self):
        self.cache = MemcachedCache([f"{constants.MEMCACHED_HOST}:{constants.MEMCACHED_PORT}"],
                                    default_timeout=constants.MEMCACHED_TIMEOUT)
        self.redis = redis.Redis(host=constants.REDIS_HOST, port=constants.REDIS_PORT)


class CacheHelper:
    """
    Helper class with methods for managing redis/memcache operations
    """

    def validate_local_cache_key(self, cache_type, cache_obj):
        """
        Checks and raises errors if types are mismatched between what is being queried and the controller being used

        :param cache_type: string. Either 'local' or 'redis'
        :param cache_obj: Redis instance | Memcached instance
        :return: bool | Error
        """
        if cache_type not in ['local', 'redis']:
            raise ValueError("Need to provide cache type to be either local or redis")
        if cache_type == 'local' and not isinstance(cache_obj, MemcachedCache):
            raise TypeError("local cache_type does not match cache_obj type!")
        elif cache_type == 'redis' and not isinstance(cache_obj, redis.Redis):
            raise TypeError('redis cache_type does not match cache_obj type')

        return True

    def check_key_in_redis_cache(self, key, r_cache):
        """
        Check if key exists in redis and create appropriate messages
        :param key: any type
        :param r_cache: redis instance
        :return: tuple key value, string message | bool, string message
        """
        if not key:
            raise ValueError("Need to provide key")

        if self.validate_local_cache_key('redis', r_cache):
            key_check = r_cache.get(key)
            if not key_check:
                message = "<br>Key not found in redis cache"
                return False, message

            message = "<br><b>Key found in redis cache</b>"
            # Need to decode bytestring returned by redis library
            return key_check.decode(), message

    def check_key_in_local_cache(self, key, l_cache):
        """
        Check if key exists in local memcache and generate appropriate messages
        :param key: any type
        :param l_cache: memcache instance
        :return: tuple key value, string message | bool, string message
        """
        if not key:
            raise ValueError("Need to provide key")

        if self.validate_local_cache_key('local', l_cache):
            key_check = l_cache.get(key)
            if not key_check:
                message = "<br>Key not found in local cache"
                return False, message

            message = "<br><b>Key found in local cache</b>"
            return key_check, message

    @staticmethod
    def get_key_logic(key, l_cache, r_cache ):
        """
        Static method to handle repetitve logic for key/value data
        :param key: any type
        :param l_cache: memcached instance
        :param r_cache: redis instance
        :return:tuple key value, string message
        """
        ch = CacheHelper()
        # First check if key exists in local cache
        value, l_message = ch.check_key_in_local_cache(key, l_cache)
        if not value:
            # Since it doesn't exist locally, check in redis
            value, r_message = ch.check_key_in_redis_cache(key, r_cache)
            if value:
                # Key found in redis. Gather messages and set it locally in memcache
                message = l_message + r_message
                l_cache.set(key, value)
            else:
                # Nothing to do here except for returning messages since no key was found
                message = l_message + r_message
        else:
            message = l_message
        return value, message


