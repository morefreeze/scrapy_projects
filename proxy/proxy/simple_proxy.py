# coding: utf-8
import csv
import sys
import datetime
from tqdm import tqdm
import urllib
import urllib2


def test_url(opener, url):
    try:
        resp = opener.open(url, timeout=TIMEOUT)
        if resp and resp.code == 200:
            return True
    except Exception as e:
        print e
    return False

candidate_proxies = [
    # 'http://110.84.128.143:3128',
    # 'http://39.163.54.101:80',
    # 'http://175.17.14.5:8888',
    'http://89.19.193.1:3128',
    'http://166.62.86.208:80',
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
for proxy in candidate_proxies:
    print "Trying HTTP proxy %s" % proxy
    ph = urllib2.ProxyHandler({'http': proxy})
    opener = urllib2.build_opener(ph)
    gfw_succ = False
    succ = False
    for url in tqdm(gfw_urls):
        if test_url(opener, url):
            gfw_succ = True
            break
    for url in tqdm(normal_urls):
        if test_url(opener, url):
            succ = True
            break
    if gfw_succ:
        print '%s is good for gfw' % (proxy)
    if succ:
        print '%s is good' % (proxy)
