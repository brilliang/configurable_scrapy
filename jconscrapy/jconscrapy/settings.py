# -*- coding: utf-8 -*-

# Scrapy settings for jconscrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'jconscrapy'

SPIDER_MODULES = ['jconscrapy.spiders']
NEWSPIDER_MODULE = 'jconscrapy.spiders'

TELNETCONSOLE_ENABLED = False

USER_AGENT = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"

DOWNLOAD_DELAY = 1.0
