# coding: utf-8

import time
import hashlib
import urllib

from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.utils.response import get_base_url
from urlparse import urljoin

from constants import *
from jconscrapy.items import JconscrapyItem
from jconscrapy.spiders.config import ConfigurableCrawlerConfigure

class ConfigurableSpider(Spider):

    name = 'confspider'

    def __init__(self, config, config_file, **kwargs):
        super(Spider, self).__init__(**kwargs)
        self.config = ConfigurableCrawlerConfigure(config, config_file).config

    def start_requests(self):
        """
        start job from here
        """
        conf_links = self.config[LINKS]
        for conf_link in conf_links:
            meta = {
                META_LINK: conf_link,
                META_ITEM: {}
            }
            for url in conf_link[EXTRACTOR].extract(None):
                yield Request(url=url, meta=meta, callback=self.traversal)

    def traversal(self, response):
        """"
        links遍历器
        对一个link节点， type & value 是从上级页面的文本中，抽取自己url的方法
        子links 和 子 items 节点描述的是这个链接打开的页面上，再次抽取其他信息的方法
        """
        if META_LINK not in response.meta:
            return

        meta = response.meta
        conf_link = meta[META_LINK]

        # 抽取item
        item = make_item(response, conf_link)
        if item:
            response.meta[META_ITEM] = item
            yield JconscrapyItem(item, self)

        # 处理翻页链接
        if PAGE_LINK in conf_link:
            for url in conf_link[PAGE_LINK][EXTRACTOR].extract(response):
                url = qualify_link(response, url)
                yield Request(url=url,
                              meta={META_LINK: conf_link, META_ITEM: item},
                              callback=self.traversal)

        # 遍历下一级
        if LINKS in conf_link:
            for child_link in conf_link[LINKS]:
                has_item = child_link.get(ITEM)
                for url in child_link[EXTRACTOR].extract(response):
                    url = qualify_link(response, url)
                    if has_item and is_dup(url):
                        log.msg("url duplication: %s" %(url,), logLevel=log.INFO)
                        continue

                    rel_url = None
                    if child_link.get(RENDER):
                        rel_url = url
                        url = WEBDRIVER_PROXY + urllib.quote_plus(url)
                    yield Request(url=url,
                                  meta={META_LINK: child_link, META_ITEM: item, URL: rel_url},
                                  callback=self.traversal)


def make_item(response, conf_link):
    """ 抽取item """
    if ITEM not in conf_link:
        return {}

    rel_url = response.meta.get(URL)
    if rel_url:
        response = response.replace(url=rel_url)

    item = {
        URL: response.url,
        TYPE: conf_link[DOC] if DOC in conf_link else ITEM_MAIN,
    }

    item.update(response.meta.get(META_ITEM, {}))
    item.update({k: v[EXTRACTOR].extract(response) if v.get(LIST)
                    else ' '.join(v[EXTRACTOR].extract(response))
                 for k, v in conf_link[ITEM].items()})

    if not item.get('content'):  # content字段为空：配置的模板没有在response.body上命中
        log.msg("item content missed. ", logLevel=log.WARNING)
        # item['body'] = ''.join(response.xpath('//body').extract())
    if 'image_urls' in item:
        item['image_urls'] = [qualify_link(response, url) for url in item['image_urls']]

    return add_merge_info(response, conf_link, item)


def add_merge_info(response, conf_link, item):
    if DOC not in item or conf_link[DOC] == ITEM_MAIN:     # main doc
        item[ITEM_ID] = gen_id(response.url)
        return item
    elif ITEM_ID in response.meta[META_ITEM]:
        doc_id = response.meta[META_ITEM][ITEM_ID]
        return {ITEM_ID: doc_id, conf_link[DOC]: item}
    else:
        log.msg("no doc_id found!", logLevel=log.ERROR)


def gen_id(url):
    url += str(time.time())
    return hashlib.md5(url).hexdigest()

def qualify_link(response, link):
    return urljoin(get_base_url(response), link)
