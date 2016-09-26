# -*- coding: utf-8 -*-
import scrapy
from items import BookItem


def safe_list_get(l, idx, default=''):
    return l[idx] if len(l) > idx else default


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.cn"]
    start_urls = (
        'https://www.amazon.cn/s/?node=1841471071&ie=UTF8',
    )

    def start_requests(self):
        return [scrapy.FormRequest(self.start_urls[0], callback=self.parse_book_follow_next_page)]

    def parse_book_follow_next_page(self, response):
        lis = response.xpath('//ul[contains(@class, "s-result-list")]/li')
        for li in lis:
            item = BookItem()
            item['title'] = safe_list_get(li.xpath('.//h2/@data-attribute').extract(), 0, '')
            if item['title'] == '':
                continue
            item['author'] = safe_list_get(li.xpath('.//div[@class="a-row a-spacing-none"]/span/text()').extract(), 0, 'Unknown')
            item['price'] = li.xpath('.//span[contains(@class, "s-price")]/text()').extract()
            item['rating'] = float(safe_list_get(li.xpath('.//i[contains(@class, "a-icon-star")]/span/text()').re('[\d\.]+'), 0, 0.0))
            item['rating_num'] = int(safe_list_get(li.xpath('.//a[contains(@class, "a-size-small")]/text()').re('\d+'), 0, 0))
            yield item

        next_page = response.xpath('//a[@id="pagnNextLink"]/@href')
        self.logger.debug(next_page)
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_book_follow_next_page)
