#! /usr/bin/env python
# -*- coding: UTF8 -*-


from jsonschema import validate

item_conf = {
    "type": {
        "type": "const",
        "value": "main"
    },
    "title": {
        "type": "xpath",
        "value": "//title/text()"
    },
}

link_array = [
    {
        "type": "const",
        "value": "http://ent.163.com/",
        "links": [
            {
                "type": "link_extractor",
                "value": {"allow": "http://ent.163.com/\\d+/\\d+/\\d+/[0-9a-zA-Z]+.html"},
                "item": item_conf
            }
        ]
    }
]

######################## schema below ###############################

link_extractor_schema = {
    "type":"object",
    "properties":{
        "allow":{
            "type":"string"
        },
        "deny":{
            "type":"string"
        }
    }
}

item_schema = {
    "type": "object",
    "patternProperties": {
        "[_a-zA-Z]\\w*": {
            "properties": {
                "type": {
                    "type": "string"
                },
                "value": {
                    "type": "string"
                },
            },
            "required": ["type", "value"]
        }
    }
}

print validate(item_conf, item_schema)

link_array_schema = {
    "id": "link_array_schema",
    "type": "array",
    "items": {
        "properties": {
            "type": {
                "type": "string",
            },
            "value": {
                "anyOf":[
                    {"type": "string"},
                    {"type": "object",
                     "properties":{
                         "allow":{
                             "type":"string"
                         }
                     }}
                ]
            },
            "item": item_schema,
            "links": {
                "$ref":"link_array_schema"
            }
        },
        "required": ["type", "value"]
    }

}

print validate(link_array, link_array_schema)


