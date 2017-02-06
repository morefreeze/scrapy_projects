# coding: utf-8
from proxy.checker import ProxyChecker
from scrapy.exceptions import DropItem
from db import RedisPool
import settings


class DuplicatesPipeline(object):

    """check ip whether duplicate with redis"""
    def __init__(self, redis_host, redis_port, redis_db):
        """get a redis connection
        """
        self.conn = RedisPool.get_pool(redis_host, redis_port, redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        redis_host = crawler.settings.get('REDIS_HOST')
        redis_port = crawler.settings.get('REDIS_PORT')
        redis_db = crawler.settings.get('REDIS_DB')
        return cls(redis_host, redis_port, redis_db)

    def process_item(self, item, spider):
        """return ip is duplicate or not

        :item: crawl item including host port
        :returns: return item or DropItem
        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        if self.conn.sismember(settings.HOST_S, host) or self.dup_in_queue(host):
            raise DropItem('%s, cause duplicate' % (host))
        else:
            return item

    def dup_in_queue(self, host):
        set_list = [settings.NORMAL_S, settings.GFW_S]
        for set_name in set_list:
            if self.conn.sismember(set_name, host):
                return True
        return False


class RedisPipeline(object):
    """If item has 'normal' or 'gfw' then store to redis
    """
    def __init__(self, redis_host, redis_port, redis_db):
        """get a redis connection
        """
        self.conn = RedisPool.get_pool(redis_host, redis_port, redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        redis_host = crawler.settings.get('REDIS_HOST')
        redis_port = crawler.settings.get('REDIS_PORT')
        redis_db = crawler.settings.get('REDIS_DB')
        cls.host_s = crawler.settings.get('HOST_S')
        return cls(redis_host, redis_port, redis_db)

    """save to redis"""
    def process_item(self, item, spider):
        """save to redis and return item

        :item: crawl item including host port
        :returns: return item or DropItem
        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        self.conn.sadd(self.host_s, host)
        return item
