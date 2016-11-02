# coding: utf-8
import csv
import sys
import datetime
from tqdm import tqdm
import urllib
import urllib2
import re
import scrapy
import redis

from pipelines import NormalIPPipeline


class IP84Spider(scrapy.Spider):
    name = 'ip_spider'
    IP_REGEX = re.compile('\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}\
(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b')
    start_urls = ['http://ip84.com/dl']

    """Get proxy ip from url"""

    def __init__(self):
        """"""

    def parse(self, response):
        """parse crawl page

        :response: TODO
        :returns: None

        """
        # debug
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        for i in range(1, 2):
            yield scrapy.Request(response.request.url + '/%s' % (i), callback=self.parse_ip)

    def parse_ip(self, response):
        """parse ip

        :response: TODO
        :returns: TODO

        """
        for tr in response.xpath('//table[@class="list"]//tr'):
            tds = tr.xpath('td/text()')
            if len(tds) > 2:
                yield {'ip': tds[0].extract(), 'port': tds[1].extract()}
