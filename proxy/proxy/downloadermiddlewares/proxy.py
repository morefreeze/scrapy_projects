# -*- coding: utf-8 -*-
import logging
import random
from scrapy.http import Request
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from db import RedisPool


class ProxyMiddleware(HttpProxyMiddleware):
    """use random proxy"""
    proxy_list = []

    @classmethod
    def from_crawler(cls, crawler):
        """connect redis

        :crawler: TODO
        :returns: TODO

        """
        redis_host = crawler.settings.get('REDIS_HOST')
        redis_port = crawler.settings.get('REDIS_PORT')
        redis_db = crawler.settings.get('REDIS_DB')
        normal_key = crawler.settings.get('NORMAL_KEY')
        conn = RedisPool.get_pool(redis_host, redis_port, redis_db)
        cls.proxy_list = conn.lrange(normal_key, 0, -1)
        return cls()

    def process_request(self, request, spider):
        """record this page
        """
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = 'http://%s' % (proxy)
            logging.debug('use proxy %s' % (proxy))
