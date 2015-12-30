# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import time

import scrapy
from scrapy.item import Item
from jconscrapy.spiders.constants import SPIDER, MEDIA_TYPE


class JconscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    def __setitem__(self, key, value):
        self._values[key] = value
        self.fields[key] = {}

    def __init__(self, items, spider):
        Item.__init__(self)
        for k, v in items.items():
            self[k] = v

        self[SPIDER] = {
            'name': spider.name,
            'site': spider.conf_name,
            'ctime': int(time.time()),
        }
