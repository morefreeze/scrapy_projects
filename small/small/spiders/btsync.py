# -*- coding: utf-8 -*-
import scrapy


class BtsyncSpider(scrapy.Spider):
    name = "btsync"
    allowed_domains = ["btsynckeys.com/"]

    def start_requests(self):
        for i in range(0, 621, 10):
            url = 'http://btsynckeys.com/%s' % (i)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        trs = response.xpath('//table/tbody/tr')
        for tr in trs:
            tds = tr.xpath('./td')
            name, secret, _, create_time, peers = tds
            yield {
                'name': name.xpath('./text()').extract()[0],
                'secret': secret.xpath('./text()').extract()[0],
                'create_time': create_time.xpath('./text()').extract()[0],
                'peers': peers.xpath('./text()').extract()[0],
            }
