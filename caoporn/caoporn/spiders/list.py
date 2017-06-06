# -*- coding: utf-8 -*-
import scrapy
import pymongo
import datetime
from caoporn.items import VideoItem

def get_default(arr, idx, default_value):
    """get arr[idx] or return default_value
    """
    try:
        return arr[idx]
    except IndexError:
        return default_value

def convert_time_len(tl):
    sec = 0
    for x in tl.split(':'):
        sec = sec * 60 + int(x)
    return sec

class ListSpider(scrapy.Spider):
    name = "list"
    allowed_domains = ['caoporn.com', 'caomoo.com']
    # find from mongo
    start_url = 'http://101.caomoo.com/videos?page=1'
    max_page = 1000

    def __init__(self):
        self.page_cnt = 0

    # checkpoint is always last complete parsing page url, so start with it will
    # repeat parse these items again
    def start_requests(self):
        mongo_uri=self.crawler.settings.get('MONGO_URI')
        mongo_db=self.crawler.settings.get('MONGO_DB')
        client = pymongo.MongoClient(mongo_uri)
        db = client[mongo_db]
        collection_name = 'video'
        newest_videos = db[collection_name].find().sort([('$natural', -1)]).limit(10)
        self.newest_vids = {v['hash'] for v in newest_videos}
        return [scrapy.Request(url=self.start_url, callback=self.parse_video)]

    def parse(self, response):
        pass

    def parse_video(self, response):
        touch_newest = False
        for vid in response.xpath('//div[@class="video_box"]'):
            item = VideoItem()
            item['name'] = get_default(vid.xpath('a/img/@title').extract(), 0, '')
            item['url'] = response.urljoin(get_default(vid.xpath('a/@href').extract(), 0, ''))
            item['hash'] = vid.xpath('a/@href').re('/video[0-9]*/([0-9a-f]+)/')[0]
            touch_newest = touch_newest or item['hash'] in self.newest_vids
            item['cover'] = response.urljoin(get_default(vid.xpath('a/img/@src').extract(), 0, ''))
            item['length'] = convert_time_len(get_default(vid.xpath('div[@class="box_left"]/text()').extract(), 0, '00:00').strip())
            item['views'] = get_default(vid.xpath('div[@class="box_right"]/text()').re('[0-9]+'), 0, 0)
            item['is_hd'], item['is_private'] = False, False
            for img_src in vid.xpath('img/@src').extract():
                item['is_hd'] = item['is_hd'] or 'hd.png' in img_src
                item['is_private'] = item['is_private'] or 'private-video.png' in img_src
            item['_create_time'] = datetime.datetime.now()
            yield item

        next_url = response.xpath('//div[@class="pagination"]/ul/li[position()=last()]/a[@class="prevnext"]/@href').extract()
        if len(next_url) > 0:
            if self.page_cnt < self.max_page:
                self.log(next_url[-1])
                yield scrapy.Request(next_url[-1], callback=self.parse_video)
