# coding: utf8

import logging

from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

import constants

logger = logging.getLogger(__name__)

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

        return filter(lambda x: self.filter(x) is not None, extr)

    def const(self, response):
        return [self.value]

    def filter(self, one):
        if one:
            return one

    def xpath(self, response):
        """
        抽取所有命中xpath的部分
        """
        try:
            return [x.strip() for x in response.xpath(self.value).extract()]
        except:
            logger.exception('valid xpath value:%s' % (self.value,))
            raise


class ItemExtractor(BaseExtractor):
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
            logger.exception('valid xpath n value:%s %d' % (xpath, n))
            raise

    def xpath_reg(self, response):
        """
        在命中xpath的元素中再使用正则表达式抽取
        """
        try:
            return response.xpath(self.value[0]).re(self.value[1])
        except:
            logger.exception('valid xpath-re value:%s' % (self.value,))
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
