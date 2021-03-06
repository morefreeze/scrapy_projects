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


class KDLSpider(scrapy.Spider):
    name = 'kuaidaili_spider'
    IP_REGEX = re.compile('\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}\
(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b')
    start_urls = [
        'http://www.kuaidaili.com/free/inha/',
        'http://www.kuaidaili.com/free/intr/',
        'http://www.kuaidaili.com/free/outha/',
        'http://www.kuaidaili.com/free/outtr/',
    ]

    """Get proxy ip from url"""

    def __init__(self, page=2):
        """"""
        self.page = int(page)

    def parse(self, response):
        """parse crawl page

        :response: TODO
        :returns: None

        """
        # debug
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        for i in range(1, self.page+1):
            yield scrapy.Request(
                response.request.url + '%s' % (i),
                self.parse_ip,
                dont_filter=True,
            )

    def parse_ip(self, response):
        """parse ip

        :response: TODO
        :returns: TODO

        """
        for tr in response.xpath('//table//tr'):
            tds = tr.xpath('td/text()')
            if len(tds) > 2:
                yield {'ip': tds[0].extract(), 'port': tds[1].extract()}
