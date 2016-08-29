# coding: utf-8
import sys
import datetime
from tqdm import tqdm
import urllib
import urllib2
import redis


class IPChecker(object):
    TIMEOUT = 3

    """Get from redis and check ip"""

    def __init__(self, opener):
        """
        :opener: OpenerDirector which can be has a ProxyHandler
        """
        self.opener = opener

    def check_url(self, url):
        """try to fetch url to judge opener is worked

        :url: url to check
        :returns: {succ: True, lag: 10(ms)}
        """
        try:
            resp = self.opener.open(url, timeout=self.TIMEOUT)
            if resp and resp.code == 200:
                return True
        except Exception as e:
            print e
        return False
