# -*- coding: utf-8 -*-
import logging
import os
import scrapy
import simplejson
import duokan.dkbson as dk
from duokan.items import BookInfo, IssItem

logger = logging.getLogger('duokan')

class FileSaverMixin(object):

    def parse_book_info(self, response):
        book_info = simplejson.loads(dk.decode(response.body))
        url_dir = os.path.join('url', book_info['book_id'])
        os.makedirs(url_dir, exist_ok=True)

    def parse_page(self, response):
        meta = response.request.meta
        dir = os.path.join('url', meta['book_id'])
        page_info = simplejson.loads(dk.decode(response.body))
        with open(os.path.join(dir, meta['page_id']), 'w') as f:
            f.write(page_info['url'])


class BaseSpider(scrapy.Spider, FileSaverMixin):
    name = 'base'
    allowed_domains = ['duokan.com']
    cookie = None
    save_file = False

    def parse_book_info(self, response):
        if response.status != 200:
            return
        if self.save_file:
            super().parse_book_info(response)
        book_info = simplejson.loads(dk.decode(response.body))
        yield BookInfo({'id': book_info['book_id'], 'data': book_info})
        for idx, page in enumerate(book_info['pages']):
            yield scrapy.Request('http://www.duokan.com/reader/page/%s/%s?trait=medium' % (book_info['book_id'], page['page_id']),
                                 cookies=self.cookie,
                                 callback=self.parse_page,
                                 meta={'book_id': book_info['book_id'], 'page_id': page['page_id'], 'page_num': idx},
                                )

    def parse_page(self, response):
        req = response.request
        if response.status != 200:
            logger.warning('no page content, meta[%s]' % (req.meta))
            return
        page_info = simplejson.loads(dk.decode(response.body))
        if page_info.get('status') != 'ok':
            logger.warning('page_info is not ok[%s]' % (page_info))
            return
        if self.save_file:
            super().parse_page(response)
        return
        yield IssItem({
            'book_id': req.meta['book_id'],
            'page_id': req.meta['page_id'],
            'page_num': req.meta['page_num'],
            'url': page_info['url'],
        })
        yield scrapy.Request(page_info['url'],
                             cookies=self.cookie,
                             callback=self.save_page,
                             meta=req.meta,
                             dont_filter=True,
                            )
