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
        """
        redis_host = crawler.settings.get('REDIS_HOST')
        redis_port = crawler.settings.get('REDIS_PORT')
        redis_db = crawler.settings.get('REDIS_DB')
        normal_s = crawler.settings.get('NORMAL_S')
        conn = RedisPool.get_pool(redis_host, redis_port, redis_db)
        cls.proxy_list = list(conn.smembers(normal_s))
        return cls()

    def process_request(self, request, spider):
        """record this page
        """
        if 'next_use_proxy' in request.meta and self.proxy_list and len(self.proxy_list) > 0:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = 'http://%s' % (proxy)
            logging.debug('use proxy %s' % (proxy))
        request.meta['next_use_proxy'] = True
