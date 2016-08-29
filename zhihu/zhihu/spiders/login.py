# -*- coding: utf-8 -*-
import scrapy


class LoginSpider(scrapy.Spider):
    name = "login"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        'https://www.zhihu.com/login/email',
    ]

    def parse(self, response):
        url='https://www.zhihu.com/login/email'
        xsrf=response.xpath('//div[@class="view view-signin"]//input[@name="_xsrf"]/@value').extract()
        return scrapy.FormRequest(
            url=url,
            formdata={'email': 'congming789@gmail.com',
                      'password':'',
                      'remember_me': 'true',
                      '_xsrf': xsrf[0],
                     },
            callback=self.after_login
        )

    def after_login(self, response):
        print response.body
