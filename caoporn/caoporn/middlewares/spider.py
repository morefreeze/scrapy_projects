# -*- coding: utf-8 -*-
import pymongo
from scrapy.http import Request

class CheckPointSpider(object):
    """record check point to mongo"""

    collection_name = 'checkpoint'
    def process_spider_output(self, response, result, spider):
        """record this page
        """
        mongo_uri=spider.crawler.settings.get('MONGO_URI')
        mongo_db=spider.crawler.settings.get('MONGO_DB')
        client = pymongo.MongoClient(mongo_uri)
        db = client[mongo_db]
        def add_field(request, response):
            if isinstance(request, Request):
                db[self.collection_name].update_one(
                    {},
                    {'$set': {'page_url': response.request.url}},
                    upsert=True)
            return True
        ret = [req for req in result if add_field(req, response)]
        client.close()
        return ret
