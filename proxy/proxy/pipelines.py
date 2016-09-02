# coding: utf-8
import sys
import datetime
from tqdm import tqdm
import urllib
import urllib2
import logging
import random
from scrapy.exceptions import DropItem
from db import RedisPool


class ProxyChecker(object):
    TIMEOUT = 5

    """Get from redis and check ip"""

    def __init__(self, ip, timeout=None):
        """
        :ip: TODO
        :returns: TODO

        """
        ph = urllib2.ProxyHandler({'http': ip})
        self.opener = urllib2.build_opener(ph)
        if timeout is not None:
            self.TIMEOUT = timeout

    def check_url(self, url):
        """try to fetch url to judge opener is worked

        :url: url to check
        :returns: {succ: True, lag: 10(ms)}
        """
        try:
            resp = self.opener.open(url, timeout=self.TIMEOUT)
            if resp and resp.code == 200:
                succ = True
        except Exception as e:
            succ = False
            logging.warning('check url(%s) throught proxy(%s) error: %s' % (url, self.opener.handlers[0].proxies, e))
        return {'succ': succ}


class NormalIPPipeline(object):
    url_list = [
        'http://www.baidu.com',
        'http://weibo.com',
        'http://zhihu.com',
        'http://tower.im',
        'http://www.acfun.tv',
    ]
    factor = 0.4

    def process_item(self, item, spider):
        """return ip is valid or not
        :returns: TODO

        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        checker = ProxyChecker(host)
        cnt = 0
        n = len(self.url_list)
        rint = range(n)
        random.shuffle(rint)
        for index, url_idx in enumerate(rint):
            url = self.url_list[url_idx]
            ret = checker.check_url(url)
            if ret.get('succ', False):
                cnt += 1
            if index-cnt >= n * (1-self.factor):
                break
        if n * self.factor < cnt:
            item['normal'] = True
        return item


class LadderIPPipeline(object):
    url_list = [
        'http://www.twitter.com',
        'http://www.google.com',
        'http://www.facebook.com',
        'http://www.youtube.com',
        'http://www.blogger.com',
    ]
    factor = 0.4

    def process_item(self, item, spider):
        """return ip is valid or not
        :returns: TODO

        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        checker = ProxyChecker(host, 8)
        cnt = 0
        n = len(self.url_list)
        rint = range(n)
        random.shuffle(rint)
        for index, url_idx in enumerate(rint):
            url = self.url_list[url_idx]
            ret = checker.check_url(url)
            if ret.get('succ', False):
                cnt += 1
            if cnt >= n * self.factor:
                break
        if n * self.factor < cnt:
            item['gfw'] = True
        return item


class DuplicatesPipeline(object):
    IP_SET = 'ip'

    """check ip whether duplicate with redis"""
    def __init__(self, redis_host, redis_port, redis_db):
        """get a redis connection
        :returns: TODO

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

        :item: TODO
        :spider: TODO
        :returns: TODO

        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        if self.conn.sismember('ip', host):
            raise DropItem('%s, cause duplicate' % (host))
        else:
            self.conn.sadd(self.IP_SET, host)
            return item


class RedisPipeline(object):
    def __init__(self, redis_host, redis_port, redis_db):
        """get a redis connection
        :returns: TODO

        """
        self.conn = RedisPool.get_pool(redis_host, redis_port, redis_db)

    @classmethod
    def from_crawler(cls, crawler):
        redis_host = crawler.settings.get('REDIS_HOST')
        redis_port = crawler.settings.get('REDIS_PORT')
        redis_db = crawler.settings.get('REDIS_DB')
        cls.normal_key = crawler.settings.get('NORMAL_KEY')
        cls.gfw_key = crawler.settings.get('GFW_KEY')
        return cls(redis_host, redis_port, redis_db)

    """save to redis"""
    def process_item(self, item, spider):
        """save to redis and return item

        :item: TODO
        :spider: TODO
        :returns: TODO

        """
        if 'ip' not in item:
            raise DropItem('')
        port = item.get('port', 80)
        host = '%s:%s' % (item['ip'], port)
        if item.get('normal', False):
            self.conn.rpush(self.normal_key, host)
        if item.get('gfw', False):
            self.conn.rpush(self.gfw_key, host)
        return item


random.seed()
