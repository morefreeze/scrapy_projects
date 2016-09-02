# coding: utf-8
import redis


class RedisPool(object):

    @classmethod
    def get_pool(cls, redis_host, redis_port, redis_db):
        """build a redis connection
        :returns: a valid connection

        """
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        return redis.Redis(connection_pool=pool)
