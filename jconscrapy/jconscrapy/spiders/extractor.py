# coding: utf8

import json
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

import constants
from jconscrapy.common_utils import getLogger

logger = getLogger(__name__)

class BaseExtractor(object):
    def __init__(self, etype, value, others=None):
        self.extractor_type = etype
        self.value = value
        self.vars = others

    def __str__(self):
        return self.extractor_type + ':' + str(self.value)

    def __repr__(self):
        return self.__str__()

    def extract(self, response):
        try:
            extr = getattr(self, self.extractor_type)(response)
        except:
            logger.exception("extractor {0} error".format(self.value))
            return []

        return filter(lambda x: self.filter(x), extr)

    def const(self, response):
        return [self.value]

    def filter(self, one):
        return bool(one)

    def xpath(self, response):
        """
        抽取所有命中xpath的部分
        """
        try:
            return [x.strip() for x in response.xpath(self.value).extract()]
        except:
            logger.error('valid xpath value:%s' % (self.value,))
            raise


class ItemExtractor(BaseExtractor):

    def extract_item(self, response):
        rst = self.extract(response)
        if constants.FORMAT not in self.vars:
            return ' '.join(rst)
        elif self.vars[constants.FORMAT] == constants.LIST:
            return rst
        elif self.vars[constants.FORMAT] == constants.TIMESTAMP:
            # todo timestamp parse
            return ' '.join(rst)
        else:
            raise Exception('format %s not supported.' % self.vars[constants.FORMAT])

    def xpath_n(self, response):
        """
        抽取命中xpath后的第n个元素
        """
        xpath = self.value[0]
        n = self.value[1]
        try:
            result = response.xpath(xpath).extract()
            return [result[n]] if len(result) >= n else []
        except:
            logger.error('valid xpath n value:%s %d' % (xpath, n))
            raise

    def xpath_reg(self, response):
        """
        在命中xpath的元素中再使用正则表达式抽取
        """
        try:
            return response.xpath(self.value[0]).re(self.value[1])
        except:
            logger.error('valid xpath-re value:%s' % (self.value,))
            raise


class FLinksExtractor(BaseExtractor):
    def const_list(self, response):
        return self.vars.get(constants.VALUE, [])

    def link_extractor(self, response):
        """
        使用scrapy自带的LxmlLinkExtractor抽取链接
        """
        allow = self.value.get('allow', ())
        deny = self.value.get('deny', ())
        links = LxmlLinkExtractor(allow=allow, deny=deny).extract_links(response)
        return [i.url.strip() for i in links]

    def meta_replace(self, response):
        meta_item = response.meta.get(constants.META_ITEM)
        return [self.value.format(**meta_item)]


if __name__ == '__main__':
    e = FLinksExtractor('const', 'abc', None)
    print e.extract(None)
