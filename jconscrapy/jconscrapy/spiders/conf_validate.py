#!/usr/env/bin python
# coding=utf8

import json
from ycrawler.spiders import constants

ITEM_TYPE_SET = set([
    'const', 'xpath', 'xpath_n', 'xpath_reg', 'jsonp',
])

LINK_TYPE_SET = set([
    'const', 'const_list', 'link_extractor', 'meta_replace', 'xpath'
])


class ConfError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def validate_item(value):
    if not isinstance(value, dict):
        raise ConfError("item value should be a dict")

    for k, v in value.items():
        if not isinstance(v, dict):
            raise ConfError("{0} extractor should be a dict".format(k))
        must_key = 0
        for item_key, item_value in v.items():
            if item_key == constants.TYPE:
                must_key += 1
                if item_value not in ITEM_TYPE_SET:
                    raise ConfError("item type error for key=" + k)
            elif item_key == constants.VALUE:
                must_key += 1
        if must_key < 2:
            raise ConfError("{t} or {v} missing for item conf={ok}:{ov}".
                            format(t=constants.TYPE, v=constants.VALUE, ok=k, ov=json.dumps(v)))


def validate_one_link(link):
    if not isinstance(link, dict):
        raise ConfError(r"link value should be a dict. cur link is " + json.dumps(link))

    must_key = 0
    for k, v in link.items():
        if k == constants.TYPE:
            must_key += 1
            if v not in LINK_TYPE_SET:
                raise ConfError("link type error. current type=" + v)
        elif k == constants.VALUE:
            must_key += 1
        elif k == constants.ITEM:
            validate_item(v)
        elif k == constants.LINKS:
            validate_links(v)
        elif k == constants.PAGE_LINK:  # 将翻页去除，以下两个字段都会被去掉
            pass
        elif k == constants.DOC:
            pass
        elif k == constants.RENDER:
            pass
        else:
            raise ConfError("undefined key=" + k)

    if must_key < 2:
        raise ConfError("{t} or {v} missing for item conf".
                        format(t=constants.TYPE, v=constants.VALUE))


def validate_links(links):
    if not isinstance(links, list):
        raise ConfError("links should be a list")
    for link in links:
        validate_one_link(link)


def validate_conf(configure):
    if not isinstance(configure, dict):
        raise ConfError("configure is not a dict")

    must_key = 0
    for k, v in configure.items():
        if k == 'name':
            must_key += 1
        elif k == constants.LINKS:
            validate_links(configure.get(constants.LINKS))
