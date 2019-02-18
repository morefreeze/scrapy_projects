# -*- coding: utf-8 -*-
import scrapy
import logging
import glob
import csv
import http.cookiejar
import os
from duokan.spiders.base import BaseSpider, FileSaverMixin


logger = logging.getLogger('duokan')

class ListSpider(BaseSpider, FileSaverMixin):
    name = 'list'

    def __init__(self):
        cj = http.cookiejar.MozillaCookieJar()
        # dump cookie with cookies.txt and save as a file
        cj.load('morefreeze_all.cookie')
        self.cookie = {k.name: k.value for k in cj if k.domain.endswith('duokan.com')}
        self.left_page = {}

    def start_requests(self):
        # check _done file to detect whether book is finish
        done_dirs = {os.path.basename(os.path.dirname(dir)) for dir in glob.iglob('url/*/_done')}
        with open('duokan.csv', 'r') as f:
            r = csv.DictReader(f)
            for row in r:
                if row['uuid'] not in done_dirs:
                    yield scrapy.Request('http://www.duokan.com/reader/book_info/%s/medium' % (row['uuid']),
                                         cookies=self.cookie,
                                         callback=self.parse_book_info)

    def parse_book_info(self, response):
        super().parse_book_info(response)
        self.left_page[book_info['book_id']] = len(book_info['pages'])

    def parse_page(self, response):
        super().parse_page(response)
        self.left_page[req.meta['book_id']] -= 1

    def save_page(self, response):
        req = response.request
        if response.status != 200:
            logger.warning('no page iss, book_id[%s] page_id[%s]' % (req.meta['book_id'], req.meta['page_id']))
            return
        dir = os.path.join('data', req.meta['book_id'])
        with open(os.path.join(dir, req.meta['page_id']), 'wb') as f:
            f.write(response.body)

    # def closed(self, reason):
        # for book_id in self.left_page:
            # if self.left_page[book_id] == 0:
                # url_dir = os.path.join('url', book_id)
                # with open(os.path(url_dir, '_done'), 'w') as f:
                    # pass
