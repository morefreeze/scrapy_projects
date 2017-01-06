# -*- coding: utf-8 -*-
import scrapy
import json


def safe_list_get(l, idx, default=''):
    return l[idx] if len(l) > idx else default


class InvestmentSpider(scrapy.Spider):
    name = 'Investment'
    allow_domain = ['xiaoying.com']
    cin_fields = {
        u'预期年化': 'expected_benefit',
        u'剩余期限': 'period',
        u'项目期限': 'period',
    }

    def __init__(self, url=None, page=None):
        if not url:
            url = 'https://www.xiaoying.com/invest/list?status=COLLECT'
        if not page:
            page = 1
        self.start_url = '%s&p1=%s' % (url, page)

    def start_requests(self):
        if self.start_url:
            return [scrapy.Request(
                self.start_url,
                callback=self.parse_item_follow_next_page,
            )]

    def parse_item_follow_next_page(self, response):
        lis = response.xpath('//div[contains(@class, "card-in")]')
        for li in lis:
            item = {}
            title_line = li.xpath('.//div[contains(@class, "card-hd")]')
            title = safe_list_get(title_line.xpath('./a/text()').extract(), 0, '')
            item['title'] = title
            sub_title = ','.join(title_line.xpath('./i/text()').extract())
            item['sub_title'] = sub_title
            cin_items = li.xpath('.//ul/li')
            cin_dict = {}
            for cin_item in cin_items:
                lhs, rhs = cin_item.xpath('./span/text()').extract()
                if lhs == '' and rhs == '':
                    continue
                for (text, field_name) in self.cin_fields.items():
                    if lhs.startswith(text):
                        item[field_name] = rhs
                        break
                cin_dict[lhs] = rhs
            item['cin_items'] = cin_dict
            investing = safe_list_get(li.xpath('.//span[contains(@class, "investing")]/span/text()').extract(), 0, '')
            item['investing'] = investing
            money = safe_list_get(li.xpath('.//span[contains(@class, "surplus")]/span/text()').extract(), 0, '')
            item['money'] = money
            yield item

        pager = response.xpath('//div[contains(@class, "pagination")]')
        next_page = safe_list_get(pager.xpath('./span/following-sibling::a/@href').extract(), 0, '')
        if next_page:
            url = response.urljoin(next_page)
            yield scrapy.Request(url, callback=self.parse_item_follow_next_page)
