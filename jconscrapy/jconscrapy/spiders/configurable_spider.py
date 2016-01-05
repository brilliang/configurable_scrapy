# coding: utf-8

import time
import hashlib
import urllib

from scrapy.http import Request
from scrapy.spiders import Spider

from crawler_config import CrawlerConfigure
from constants import *
from jconscrapy.items import JconscrapyItem
from jconscrapy.common_utils import getLogger, qualify_link

logger = getLogger(__name__)


class ConfigurableSpider(Spider):
    name = 'confspider'

    def __init__(self, config, config_file, **kwargs):
        super(Spider, self).__init__(**kwargs)
        self.config = CrawlerConfigure(config, config_file).config
        self.conf_name = self.config[NAME]

    def start_requests(self):
        """
        start job from here
        """
        for conf_link in self.config[LINKS]:
            meta = {
                META_LINK: conf_link,
                META_ITEM: {}
            }
            for url in conf_link[EXTRACTOR].extract(None):
                logger.info("get a start url=%s", url)
                yield Request(url=url, meta=meta, callback=self.traversal)

    def traversal(self, response):
        """"
        links遍历器
        对一个link节点， type & value 是从上级页面的文本中，抽取自己url的方法
        子links 和 子 items 节点描述的是这个链接打开的页面上，再次抽取其他信息的方法
        """
        logger.debug("response for url=%s", response.url)
        if META_LINK in response.meta:
            conf_link = response.meta[META_LINK]
        else:
            return

        item = response.meta.get(META_ITEM, {"url": response.url})
        if ITEM in conf_link:
            item.update({k: v[EXTRACTOR].extract_item(response)
                         for k, v in conf_link[ITEM].items()})

        # 遍历下一级
        if LINKS in conf_link:
            for child_link in conf_link[LINKS]:
                for url in child_link[EXTRACTOR].extract(response):
                    url = qualify_link(response, url)
                    # todo: specialized server for rendering javascript
                    # the url should be translated in a download middleware.
                    yield Request(url=url,
                                  meta={META_LINK: child_link, META_ITEM: item},
                                  callback=self.traversal)

        # TODO 翻页链接——反正现在也没有PAGE_LINK
        if PAGE_LINK in conf_link:
            for url in conf_link[PAGE_LINK][EXTRACTOR].extract(response):
                url = qualify_link(response, url)
                logger.info("get page link, url=", url)
                yield Request(url=url,
                              meta={META_LINK: conf_link, META_ITEM: item},
                              callback=self.traversal)

        if LINKS not in conf_link and PAGE_LINK not in conf_link:
             yield JconscrapyItem(item, self)