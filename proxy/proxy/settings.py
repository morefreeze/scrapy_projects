BOT_NAME = 'proxySpider'
DOWNLOAD_DELAY = 0.25
DOWNLOAD_TIMEOUT = 7

RETRY_HTTP_CODES = [400, 500, 502, 503, 521]

DOWNLOADER_MIDDLEWARES = {
    'proxy.downloadermiddlewares.proxy.ProxyMiddleware': 200,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'random_useragent.RandomUserAgentMiddleware': 400
}
USER_AGENT_LIST = "useragents.txt"

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
EXPIRE_SECONDS = 60*60*3
