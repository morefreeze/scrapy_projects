# -*- coding: utf-8 -*-
import pymongo
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MongoPipeline(object):
    collection_name = 'video'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        """connect mongo db
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        """close mongo
        """
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].replace_one({'hash': item['hash']}, dict(item), upsert=True)
        return item

class DuplicatesPipeline(object):

    """filter out duplicate"""

    collection_name = 'video'
    def __init__(self, mongo_uri, mongo_db):
        self.item_seen = set()
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        """connect mongo db
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # load all mongo item in memory
        for item in self.db[self.collection_name].find():
            if 'hash' in item:
                self.item_seen.add(item['hash'])
            else:
                print('item: %s' % item)
        print("import mongo %d items" %(len(self.item_seen)))

    def close_spider(self, spider):
        """close mongo
        """
        self.client.close()

    def process_item(self, item, spider):
        """check item weather in item_seen
        """
        if item['hash'] in self.item_seen:
            raise DropItem('Duplicate item found: %s' %item)
        else:
            self.item_seen.add(item['hash'])
            return item
