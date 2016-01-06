#! /usr/bin/env python
# -*- coding: UTF8 -*-


import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


logger = logging.getLogger(__name__)


class Fetcher(object):

    def __init__(self):
        self.browser= webdriver.Firefox()
        self.browser.get('https://www.google.com')
        main_window = self.browser.current_window_handle


    def fetch(self, url, js_script=None):
        self._open_new_tab()
        try:
            self.browser.get(url)
            if js_script:
                self.browser.execute_script(js_script)
            return self.browser.page_source
        except:
            logger.exception("browser error when get url=%s", url)
            return "ERROR"
        finally:
            self._close_current_tab()

    def _open_new_tab(self):
        self.browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')

    def _close_current_tab(self):
        self.browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')

    def close(self):
        self.browser.close()


if __name__ == "__main__":
    f = Fetcher()
    rst = {
        "baidu":f.fetch("http://www.baidu.com"),
        "google":f.fetch("http://www.msn.com/en-sg/")
    }
    import json
    print json.dumps(rst, indent=4)
    f.close()