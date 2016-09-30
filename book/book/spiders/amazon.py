# -*- coding: utf-8 -*-
import scrapy
from items import BookItem


def safe_list_get(l, idx, default=''):
    return l[idx] if len(l) > idx else default


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    cat = None
    start_url = None
    start_urls = {
        '文学': 'https://www.amazon.cn/s/?node=1841471071&ie=UTF8',
        '经管': 'https://www.amazon.cn/s/?node=1841478071&ie=UTF8',
        '社科': 'https://www.amazon.cn/s/?node=1841479071&ie=UTF8',
        '科技': 'https://www.amazon.cn/s/?node=1841480071&ie=UTF8',
        '少儿': 'https://www.amazon.cn/s/?node=1841481071&ie=UTF8',
        '教育': 'https://www.amazon.cn/s/?node=1844551071&ie=UTF8',
        '生活': 'https://www.amazon.cn/s/?node=1844552071&ie=UTF8',
    }

    def __init__(self, cat=None, url=None):
        if cat and url:
            self.cat = cat
            self.start_url = url

    def start_requests(self):
        if self.cat and self.start_url:
            return [scrapy.Request(
                self.start_url,
                meta={'category': self.cat},
                callback=self.parse_book_follow_next_page
            )]
        return [scrapy.Request(
            url,
            meta={'category': cat},
            callback=self.parse_book_follow_next_page
        ) for cat, url in self.start_urls.items()]

    def parse_book_follow_next_page(self, response):
        lis = response.xpath('//ul[contains(@class, "s-result-list")]/li')
        for li in lis:
            item = BookItem()
            item['title'] = safe_list_get(li.xpath('.//h2/@data-attribute').extract(), 0, '')
            if item['title'] == '':
                continue
            item['author'] = safe_list_get(li.xpath('.//div[@class="a-row a-spacing-none"]/span/text()').extract(), 0, 'Unknown')
            item['price'] = li.xpath('.//span[contains(@class, "s-price")]/text()').extract()[-1]
            item['rating'] = float(safe_list_get(li.xpath('.//i[contains(@class, "a-icon-star")]/span/text()').re('[\d\.]+'), 0, 0.0))
            item['rating_num'] = int(safe_list_get(li.xpath('.//a[contains(@class, "a-size-small")]/text()').re('\d+'), 0, 0))
            item['url'] = safe_list_get(li.xpath('.//a[contains(@class, "s-access-detail-page")]/@href').extract(), 0, '')
            item['category'] = response.meta['category']
            yield item

        next_page = response.xpath('//a[@id="pagnNextLink"]/@href')
        self.logger.debug(next_page)
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_book_follow_next_page, meta=response.meta)
