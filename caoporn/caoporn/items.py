# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    hash = scrapy.Field()
    cover = scrapy.Field()
    length = scrapy.Field()
    views = scrapy.Field()
    is_hd = scrapy.Field()
    is_private = scrapy.Field()
    _create_time = scrapy.Field()

