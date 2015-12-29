# coding: utf-8

import json
import codecs
import logging

from jconscrapy.spiders.conf_validate import validate_conf
from jconscrapy.spiders.extractor import ItemExtractor, FLinksExtractor

import constants


class FocusedCrawlerConfigure:
    _config = {}

    def __init__(self, config_string, config_file):
        """
        优先使用已解析成json的配置；否则根据文件地址读取配置
        """
        self._config = json.loads(config_string, 'utf8') \
            if config_string else _read_conf_file(config_file)
        validate_conf(self._config)
        self.parse(self._config.get(constants.LINKS))

        log_msg_str = "load the conf from {cf} OK! the job is \n{job}".format(
            cf=config_file if not config_string else "json string",
            job=json.dumps(self._config,
                           ensure_ascii=True,
                           indent=4,
                           default=lambda x: repr(x) if isinstance(x, BaseExtractor) else x)
        )
        print log_msg_str
        logging.info(log_msg_str)

    @property
    def config(self):
        return self._config

    def parse(self, links):
        """
        将配置中的extractor构造出来，可在解析过程中重用而非重复创建
        """

        def _param(_cur_conf):
            return _cur_conf.get(constants.TYPE), \
                   _cur_conf.get(constants.VALUE), \
                   _cur_conf

        for link in links:
            # 从上一级页面中抽取网页链接的配置
            # print len(_param(link))
            # exit(1)
            link[constants.EXTRACTOR] = FLinksExtractor(*_param(link))

            # 在当前页面中item的配置
            item = link.get(constants.ITEM)
            if item:
                for k, v in item.items():
                    link[constants.ITEM][k][constants.EXTRACTOR] = ItemExtractor(*_param(v))

            # 在当前页面中抽取翻页链接的配置
            # TODO no more page link ???
            page_link = link.get(constants.PAGE_LINK)
            if page_link:
                link[constants.PAGE_LINK][constants.EXTRACTOR] = FLinksExtractor(page_link)

            # 在当前页面中抽取网页链接的配置
            if link.get(constants.LINKS):
                self.parse(link[constants.LINKS])


def _read_conf_file(config_file):
    with codecs.open(config_file, "r", "utf8") as f:
        try:
            return json.load(f, "utf8")
        except:
            logging.exception("json load configuration file error.")
            raise


if __name__ == '__main__':
    conf_path = "/Users/zhuliang/work/cuc/spider/crawlers/ycrawler/ycrawler/configs/ent.qq.com.json.valid"
    config = FocusedCrawlerConfigure(None, conf_path).config

    # print json.dumps(configs,
    # ensure_ascii=True,
    # indent=4,
    # default=DEFAULT_JSON_DECODER)