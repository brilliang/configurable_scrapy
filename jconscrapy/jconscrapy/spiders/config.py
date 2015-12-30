# coding: utf-8

import json
import codecs

from jconscrapy.common_utils import getLogger

from extractor import BaseExtractor, ItemExtractor, FLinksExtractor
from config_json_schema import validate_conf
from constants import *

logger = getLogger(__name__)


class ConfigurableCrawlerConfigure:
    _config = {}

    def __init__(self, config_string, config_file):
        """
        优先使用已解析成json的配置；否则根据文件地址读取配置
        """

        self._config = config_string
        self._config_file = config_file

        if self._config:
            logger.info("load conf from json string")
        else:
            with codecs.open(config_file, 'r', 'utf8') as f:
                self._config = json.load(f)
                logger.info("load conf from %s" % config_file)

        validate_conf(self._config)
        self.parse(self._config.get(LINKS))

        logger.debug(json.dumps(self._config,
                           ensure_ascii=True,
                           indent=4,
                           default=lambda x: repr(x) if isinstance(x, BaseExtractor) else x))

    @property
    def config(self):
        return self._config

    def parse(self, links):
        """
        将配置中的extractor提前构造出来，可在解析过程中重用而非重复创建
        """

        def _param(_cur_conf):
            return _cur_conf.get(TYPE), \
                   _cur_conf.get(VALUE), \
                   _cur_conf

        for link in links:
            # 从上一级页面中抽取网页链接的配置
            link[EXTRACTOR] = FLinksExtractor(*_param(link))

            # 在当前页面中item的配置
            item = link.get(ITEM)
            if item:
                for k, v in item.items():
                    link[ITEM][k][EXTRACTOR] = ItemExtractor(*_param(v))

            # 在当前页面中抽取翻页链接的配置
            # TODO add page link next time
            # TODO no more page link ???
            # page_link = link.get(PAGE_LINK)
            # if page_link:
            #     link[PAGE_LINK][EXTRACTOR] = FLinksExtractor(page_link)

            # 下一级链接的配置
            if link.get(LINKS):
                self.parse(link[LINKS])


if __name__ == '__main__':
    import os

    cur_dir = os.path.abspath(os.path.dirname(__file__))
    conf_file = os.path.join(cur_dir,
                             "../configs/youku.json")
    conf = ConfigurableCrawlerConfigure(config_string="", config_file=conf_file)

