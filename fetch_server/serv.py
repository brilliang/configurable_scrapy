#! /usr/bin/env python
# -*- coding: UTF8 -*-


import logging
from urllib import unquote

from flask import Flask
from flask import request

from py_selenium import Fetcher


logger = logging.getLogger(__name__)
app = Flask(__name__)
fetcher = Fetcher()


@app.route("/fetch")
def fetch():
    orig_url = request.args.get('url')
    url = unquote(orig_url)
    print url
    logger.info("fetch for %s", url)
    return fetcher.fetch(url)


if __name__ == '__main__':
    app.run()

