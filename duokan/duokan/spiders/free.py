# -*- coding: utf-8 -*-
import logging
import scrapy
from duokan.spiders.base import BaseSpider, FileSaverMixin

logger = logging.getLogger('duokan')

class FreeSpider(BaseSpider, FileSaverMixin):
    name = 'list'
    save_file = True

    start_urls = ['http://www.duokan.com/']
    # start_urls = ['http://www.duokan.com/special/10882']

    def parse(self, response):
        special = response.css('div.u-aimg>ul>li>a::attr(href)').extract()
        yield scrapy.Request('http://www.duokan.com%s' % (special[0]),
                             callback=self.parse2,
                            )

    def parse2(self, response):
        for book_id in response.css('ul.j-list>li::attr(data-id)').extract():
            yield scrapy.Request('http://www.duokan.com/reader/book_info/%s/medium' % (book_id),
                                 cookies=self.cookie,
                                 callback=self.parse_book_info,
                                )
