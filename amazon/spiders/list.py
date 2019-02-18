# -*- coding: utf-8 -*-
import datetime
import locale
import scrapy
from amazon.items import BookItem


def safe_list_get(l, idx, default=''):
    return l[idx] if len(l) > idx else default


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    cat = None
    start_url = None
    start_urls = {
        '文学巨匠': 'https://www.amazon.cn/s/?node=1851470071&ie=UTF8',
        '外国文学': 'https://www.amazon.cn/s/?node=1851471071&ie=UTF8',
        '秋乏冬眠': 'https://www.amazon.cn/s/?node=1851472071&ie=UTF8',
        '文艺青年': 'https://www.amazon.cn/s/?node=1851473071&ie=UTF8',
        '诺贝尔奖': 'https://www.amazon.cn/s/?node=1851474071&ie=UTF8',
    }

    def __init__(self, cat=None, url=None, node=None):
        self.cat = cat if cat else datetime.datetime.today().strftime('%Y%m%d')
        self.start_url = 'https://www.amazon.cn/s/?node=%s' % (node) if node else url

    def start_requests(self):
        if self.cat and self.start_url:
            return [scrapy.Request(
                self.start_url,
                meta={'category': self.cat},
                callback=self.parse_book_follow_next_page
            )]

    def parse_book_follow_next_page(self, response):
        lis = response.xpath('//ul[contains(@class, "s-result-list")]/li') or \
            response.xpath('//div[contains(@class, "s-result-list")]/div[contains(@class, "s-result-item")]')

    def parse_first_page(self, response):
        lis = response.xpath('//ul[contains(@class, "s-result-list")]/li')
            item['rating_num'] = int(safe_list_get(li.xpath('.//a[contains(@class, "a-size-small")]/text()').re('\d+') or \
                                                   li.xpath('.//div[contains(@class,"a-size-small")]/span[2]//span/text()').re('\d+'), 0, 0))
            item['url'] = safe_list_get(li.xpath('.//a[contains(@class, "s-access-detail-page")]/@href').extract() or \
                                        li.xpath('.//a[contains(@class, "a-link-normal")]/@href').extract(), 0, '')
            if self.allowed_domains[0] not in item['url']:
                item['url'] = self.allowed_domains[0] + item['url']
            item['category'] = response.meta['category']
            yield item

        next_page = response.xpath('//li[contains(@class, "a-last")]/a/@href') or \
            response.xpath('//a[@id="pagnNextLink"]/@href')

        next_page = response.xpath('//a[@id="pagnNextLink"]/@href') or response.xpath('//li[@class="a-last"]/a/@href')

