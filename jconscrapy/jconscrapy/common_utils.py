# coding=utf8

import os
import codecs
import json
import logging
import logging.config

log_conf_file = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "logging_conf.json"
)
with codecs.open(log_conf_file, "r", "UTF8") as f:
    logging.config.dictConfig(json.load(f))

ROOT_LOGGER_NAME = "jconscrapy"

def getLogger(logName):
    return logging.getLogger(ROOT_LOGGER_NAME if logName == '__main__' else logName)



