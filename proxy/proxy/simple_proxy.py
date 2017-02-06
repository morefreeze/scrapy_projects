# coding: utf-8
import csv
import sys
import datetime
import urllib
import urllib2
import gevent
from gevent.local import local


def test_url(opener, url):
    try:
        resp = opener.open(url, timeout=TIMEOUT)
        if resp and resp.code == 200:
            return True
    except Exception as e:
        print e
    return False

stash = local()
stash.gfw_succ = False
stash.normal_succ = False
candidate_proxies = [
    '103.4.167.230:8080',
    '220.113.26.18:8080',
]
gfw_urls = [
    'http://google.com',
    'http://facebook.com',
    'http://twitter.com',
    'http://youtube.com',
    'http://pornhub.com',
]
normal_urls = [
    'http://baidu.com',
    'http://weibo.com',
    'http://zhihu.com',
    'http://tower.im',
    'http://www.acfun.tv',
]
TIMEOUT = 3
def gfw_func(opener, url):
    if test_url(opener, url):
        stash.gfw_succ = True

def normal_func(opener, url):
    if test_url(opener, url):
        stash.normal_succ = True

for proxy in candidate_proxies:
    print "Trying HTTP proxy %s" % proxy
    ph = urllib2.ProxyHandler({'http': proxy})
    opener = urllib2.build_opener(ph)
    threads = []
    for url in gfw_urls:
        threads.append(gevent.spawn(gfw_func, opener, url))
    gevent.joinall(threads)
    threads = []
    for url in normal_urls:
        threads.append(gevent.spawn(normal_func, opener, url))
    gevent.joinall(threads)
    if stash.gfw_succ:
        print '%s is good for gfw' % (proxy)
    if stash.normal_succ:
        print '%s is good' % (proxy)
