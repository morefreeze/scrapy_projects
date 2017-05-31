import datetime


BOT_NAME = 'proxySpider'
DOWNLOAD_DELAY = 2
DOWNLOAD_TIMEOUT = 7

RETRY_HTTP_CODES = [400, 500, 502, 503, 521]

DOWNLOADER_MIDDLEWARES = {
    'proxy.downloadermiddlewares.proxy.ProxyMiddleware': 200,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'random_useragent.RandomUserAgentMiddleware': 400
}
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

ITEM_PIPELINES = {
    'proxy.pipelines.DuplicatesPipeline': 300,
    'proxy.pipelines.RedisPipeline': 800,
}

REDIS_HOST = 'localhost'
REDIS_PORT = 4149
REDIS_DB = 0
REDIS_TEST_DB = 1
REDIS_SEP = ':'
NORMAL_S = 'normal'
GFW_S = 'gfw'
HOST_S = 'host'
EXPIRE_PRE = 'expire'
EXPIRE_DELTA = datetime.timedelta(seconds=60*60*3)
