# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookInfo(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    data = scrapy.Field()

class IssItem(scrapy.Item):
    book_id = scrapy.Field()
    page_id = scrapy.Field()
    page_num = scrapy.Field()
    url = scrapy.Field()
