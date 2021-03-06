# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    date = scrapy.Field()
    author = scrapy.Field()
    author_date = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    rating_num = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
