#! /usr/bin/env python
# -*- coding: UTF8 -*-

import json
import codecs
from jsonschema import validate

# define some basic and often used data type.
str_type = {"type": "string"}
str_array_type = {
    "type": "array",
    "items": str_type
}

item_schema = {
    "type": "object",
    "patternProperties": {
        "[_a-zA-Z]\\w*": {
            "properties": {
                "type": str_type,
                "value": {
                    "oneOf": [
                        str_type,
                        str_array_type
                    ]
                },
                "format": str_type,
            },
            "required": ["type", "value"]
        }
    }
}

conf_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": str_type,
        "links": {
            "type": "array",
            "items": {
                "properties": {
                    "type": str_type,
                    "value": {
                        "oneOf": [
                            str_type,
                            str_array_type,
                            {"type": "object",
                             "properties": {
                                 "allow": str_type,
                                 "deny": str_type,
                             }}
                        ]
                    },
                    "item": item_schema,
                    "links": {
                        "$ref": "#/properties/links"
                    }
                },
                "required": ["type", "value"],
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}


def validate_conf(conf_content):
    validate(conf_content, conf_schema)


def validate_conf_file(conf_file):
    with codecs.open(conf_file, 'r', 'utf8') as f:
        validate(json.load(f), conf_schema)


if __name__ == '__main__':
    import os

    cur_dir = os.path.abspath(os.path.dirname(__file__))
    conf_file = os.path.join(cur_dir,
                             "../configs/youku.json")
    validate_conf_file(conf_file)
