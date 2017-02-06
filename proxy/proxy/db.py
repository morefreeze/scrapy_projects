# coding: utf-8
import redis
import logging
import settings


class RedisPool(object):

    @classmethod
    def get_pool(cls, redis_host, redis_port, redis_db):
        """build a redis connection
        :returns: a valid connection

        """
        try:
            pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
            return redis.Redis(connection_pool=pool)
        except Exception as e:
            logging.error('connection redis error[%s]' % (e))
            raise

def build_key(keys, sep=settings.REDIS_SEP):
    return sep.join(keys)
