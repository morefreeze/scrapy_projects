# coding: utf-8
import csv
import sys
import datetime
from tqdm import tqdm
import urllib
import urllib2
import re
import redis


class RedisQueue(object):
    HOST = 'localhost'
    PORT = 4149
    DB = 0
    PUSHED_FMT = '%s:pushed'
    POPED_FMT = '%s:poped'

    """Use redis implement a random array"""

    def __init__(self, name):
        """"""
        self.poped_name = self.POPED_FMT % (name)
        self.pushed_name = self.PUSHED_FMT % (name)
        pool = redis.ConnectionPool(host=self.HOST, port=self.PORT, db=self.DB)
        self.conn = redis.Redis(pool)

    def push(self, ip):
        """Push a ip to queue, check duplicate

        :ip: TODO
        :returns: TODO

        """
        if not self.is_dup(ip):
            self.conn.sadd(self.pushed_name, ip)

    def pop(self):
        """Pop the first ip and add it to poped
        :returns: TODO

        """
        ret = self.conn.srandmember(self.pushed_name)
        if ret:
            self.conn.smove(self.pushed_name, self.poped_name, ret)
        return ret

    def is_dup(self, ip):
        """Check duplicate of given ip

        :ip: TODO
        :returns: TODO

        """
        return self.conn.sismember(self.poped_name, ip)
