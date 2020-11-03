# -*- coding: utf-8 -*-
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
        if cat and (node or url):
            self.cat = cat
            if url:
                self.start_url = url
            else:
                self.start_url = 'https://www.amazon.cn/s/?node=%s' % (node)

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
            item['date'] = safe_list_get(li.xpath('.//div[@class="a-row a-spacing-none"][1]/span/text()').extract(), 0, 'Unknown')
            item['author'] = safe_list_get(li.xpath('.//div[@class="a-row a-spacing-none"][2]/span/text()').extract(), 0, 'Unknown')
            # price = li.xpath('.//span[contains(@class, "s-price")]/text()').extract()
            # if len(price) == 0:
            # price = li.xpath('.//span[contains(@class, "a-color-price")]/text()').extract()
            # item['price'] = price[-1] if len(price) > 0 else '-1.0'
            item['price'] = ''.join(li.xpath('.//span[contains(@class, "price")]/text()')[-3:].extract())
            item['rating'] = float(safe_list_get(li.xpath('.//i[contains(@class, "a-icon-star")]/span/text()').re('[\d\.]+'), 0, 0.0))
            item['rating_num'] = int(safe_list_get(li.xpath('.//a[contains(@class, "a-size-small")]/text()').re('\d+'), 0, 0))
            item['url'] = safe_list_get(li.xpath('.//a[contains(@class, "s-access-detail-page")]/@href').extract(), 0, '')
            item['category'] = response.meta['category']
            yield item

        next_page = response.xpath('//li[contains(@class, "a-last")]/a/@href')
        self.logger.debug(next_page)
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_book_follow_next_page, meta=response.meta)
