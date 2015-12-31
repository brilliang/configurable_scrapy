# coding: utf-8

import time
import hashlib
import urllib

from scrapy.http import Request
from scrapy.spider import Spider
from scrapy.utils.response import get_base_url
from urlparse import urljoin

from crawler_config import CrawlerConfigure
from constants import *
from jconscrapy.items import JconscrapyItem
from jconscrapy.common_utils import getLogger

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
                print url
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
            # todo yield when no deeper links found!
            yield JconscrapyItem(item, self)

        # 处理翻页链接，反正现在也没有PAGE_LINK
        # TODO add it next version
        if PAGE_LINK in conf_link:
            for url in conf_link[PAGE_LINK][EXTRACTOR].extract(response):
                url = qualify_link(response, url)
                logger.info("get page link, url=", url)
                yield Request(url=url,
                              meta={META_LINK: conf_link, META_ITEM: item},
                              callback=self.traversal)

        # 遍历下一级
        if LINKS in conf_link:
            for child_link in conf_link[LINKS]:
                # has_item = child_link.get(ITEM) # todo 忘了为啥要这样……
                # if has_item:
                #     continue
                for url in child_link[EXTRACTOR].extract(response):
                    url = qualify_link(response, url)
                    if is_dup(url):
                        logger.debug("url duplication: ", url)
                        continue

                    rel_url = None
                    # todo: specialized server for rendering javascript
                    # if child_link.get(RENDER):
                    #     rel_url = url
                    #     url = WEBDRIVER_PROXY + urllib.quote_plus(url)
                    yield Request(url=url,
                                  meta={META_LINK: child_link, META_ITEM: item, URL: rel_url},
                                  callback=self.traversal)


def is_dup(url):
    """
    在同一个scrapy进程中，有相同url去重机制
    """
    # todo 如何在多次启动、分布式运行的场景下去重和更新URL？
    return False


def make_item(response, conf_link):
    """ 抽取item """
    if ITEM not in conf_link:
        return None

    rel_url = response.meta.get(URL)
    if rel_url:
        response = response.replace(url=rel_url)

    item = {
        URL: response.url,
        TYPE: conf_link[DOC] if DOC in conf_link else ITEM_MAIN,
    }

    if META_ITEM in response.meta and \
        response.meta[META_ITEM]:
        # todo why META_ITEM could be None?
        item.update(response.meta[META_ITEM])

    # format in extractor
    item.update({k: v[EXTRACTOR].extract_item(response) for k, v in conf_link[ITEM].items()})

    if not item.get('content'):  # content字段为空：配置的模板没有在response.body上命中
        logger.warning("item content missed. url=", response.url)
        # item['body'] = ''.join(response.xpath('//body').extract())
    if 'image_urls' in item:
        item['image_urls'] = [qualify_link(response, url) for url in item['image_urls']]

    return add_merge_info(response, conf_link, item)


def add_merge_info(response, conf_link, item):
    """
    合并分页、多次渲染得到的数据
    """
    if DOC not in item or conf_link[DOC] == ITEM_MAIN:  # main doc
        item[ITEM_ID] = gen_id(response.url)
        return item
    elif ITEM_ID in response.meta[META_ITEM]:
        doc_id = response.meta[META_ITEM][ITEM_ID]
        return {ITEM_ID: doc_id, conf_link[DOC]: item}
    else:
        logger.error("no doc_id found!")


def gen_id(url):
    url += str(time.time())
    return hashlib.md5(url).hexdigest()


def qualify_link(response, link):
    return urljoin(get_base_url(response), link)
