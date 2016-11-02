BOT_NAME = 'proxySpider'
DOWNLOAD_DELAY = 0.25
DOWNLOAD_TIMEOUT = 7

DOWNLOADER_MIDDLEWARES = {
    'proxy.downloadermiddlewares.proxy.ProxyMiddleware': 200,
}

ITEM_PIPELINES = {
    'proxy.pipelines.DuplicatesPipeline': 300,
    'proxy.pipelines.NormalIPPipeline': 500,
    # 'proxy.pipelines.LadderIPPipeline': 600,
    'proxy.pipelines.RedisPipeline': 800,
}

REDIS_HOST = 'localhost'
REDIS_PORT = 4149
REDIS_DB = 0
NORMAL_KEY = 'normal'
GFW_KEY = 'gfw'
