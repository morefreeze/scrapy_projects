# coding: utf-8
import urllib
import urllib2
import logging
import settings
import time
import threading
import signal
import sys
import gevent
from gevent.lock import Semaphore
from db import RedisPool, build_key

lock = Semaphore()
class ProxyChecker(object):
    TIMEOUT = 5
    url_list = []
    ret = {}
    proxy_host = ''

    """Get from redis and check host"""

    def __init__(self, host, timeout=None):
        self.proxy_host = host
        ph = urllib2.ProxyHandler({'http': host, 'https': host})
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
            logging.warning('Check url(%s) throught proxy(%s) error: %s' % (url, self.opener.handlers[0].proxies, e))
        # TODO: return lag
        return {'succ': succ}

    """Base class of IP pipeline, use for checking IP"""
    def check_proxy(self):
        """return host is valid or not
        """
        threads = []
        self._before_check()
        for index, url in enumerate(self.url_list):
            threads.append(gevent.spawn(self._check, index, url))
        gevent.joinall(threads)
        self._after_check()

    def _check(self, index, url):
        ret = self.check_url(url)
        self._apply_rule(index, url, ret)

    def _before_check(self):
        raise NotImplementedError

    def _apply_rule(self, index, url, ret):
        raise NotImplementedError

    def _after_check(self):
        raise NotImplementedError


class NormalChecker(ProxyChecker):
    url_list = [
        'http://www.baidu.com',
        'http://weibo.com',
        'http://zhihu.com',
        'http://tower.im',
        'http://www.acfun.tv',
    ]
    factor = 0.8

    def _before_check(self):
        self.succ_cnt = 0

    def _apply_rule(self, index, url, ret):
        if ret.get('succ', False):
            with lock:
                self.succ_cnt += 1

    def _after_check(self):
        n = len(self.url_list)
        if n * self.factor <= self.succ_cnt:
            logging.debug('Check %s is successful' % (self.proxy_host))
            self.ret['ping'] = True


class LadderChecker(ProxyChecker):
    """If >=factor*n url pass then threat as valid
    """
    url_list = [
        'http://www.twitter.com',
        'http://www.google.com',
        'http://www.facebook.com',
        'http://www.youtube.com',
        'http://www.blogger.com',
    ]
    factor = 0.8

    def _before_check(self):
        self.succ_cnt = 0

    def _apply_rule(self, index, url, ret):
        if ret.get('succ', False):
            with lock:
                self.succ_cnt += 1

    def _after_check(self):
        n = len(self.url_list)
        if n * self.factor <= self.succ_cnt:
            logging.debug('Check in gfw %s is successful' % (self.proxy_host))
            self.ret['ping'] = True


def put_set(conn):
    """Check timeout host which need be checked again and put it in set
    """
    set_list = [settings.NORMAL_S, settings.GFW_S]
    while True:
        for set_name in set_list:
            while conn.scard(set_name) > 0:
                host = conn.srandmember(set_name, 0)
                expire_key = build_key([settings.EXPIRE_PRE, host])
                expire_time = conn.get(expire_key)
                expire_time = float(expire_time) if expire_time else 0
                if time.time() - expire_time >= settings.EXPIRE_SECONDS:
                    conn.sadd(settings.HOST_S, host)
                    conn.srem(set_name, host)
                    logging.debug("Push to %s set with %s" % (set_name, host))
                time.sleep(0.2)
        time.sleep(3)


def check_proxy(conn):
    """Check proxy from channel
    """
    set_dict = (
        (settings.NORMAL_S, NormalChecker),
        (settings.GFW_S, LadderChecker),
    )
    while True:
        time.sleep(0.2)
        host = conn.spop(settings.HOST_S)
        if host is None:
            continue
        for set_name, checker in set_dict:
            pc = checker(host)
            pc.check_proxy()
            if pc.ret.get('ping', False):
                conn.sadd(set_name, host)
                expire_key = build_key([settings.EXPIRE_PRE, host])
                conn.set(expire_key, time.time()+settings.EXPIRE_SECONDS)


def signal_handler(signal, frame):
    print 'Press Ctrl-C!'
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    conn = RedisPool.get_pool(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
    check_proxy_task = threading.Thread(target=check_proxy, args=(conn, ))
    put_set_task = threading.Thread(target=put_set, args=(conn, ))
    check_proxy_task.setDaemon(True)
    put_set_task.setDaemon(True)
    check_proxy_task.start()
    put_set_task.start()
    while True:
        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
