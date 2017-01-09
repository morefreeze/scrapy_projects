# -*- coding: utf-8 -*-
import scrapy
import json


def safe_list_get(l, idx, default=''):
    return l[idx] if len(l) > idx else default


class SimpleSpider(scrapy.Spider):
    name = 'Simple'
    allow_domain = ['simple.com']

    def __init__(self, url=None, page=None):
        if not url:
            url = 'https://www.simple.com/'
        if not page:
            page = 1
        self.start_url = '%s&p1=%s' % (url, page)

    def start_requests(self):
        if self.start_url:
            return [scrapy.Request(
                self.start_url,
                callback=self.parse_item_follow_next_page,
            )]

    def parse_item_follow_next_page(self, response):
        lis = response.xpath('some_xpath_of_list')
        for li in lis:
            item = {}
            title = safe_list_get(li.xpath('./title_xpath/text()').extract(), 0, '')
            item['title'] = title
            # Add other attributes
            yield item

        next_page = safe_list_get(response.xpath('next_page_xpath').extract(), 0, '')
        if next_page:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, callback=self.parse_item_follow_next_page)
