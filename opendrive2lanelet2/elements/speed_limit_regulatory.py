#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xml

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "samir.manafzadehtabriz@leidos.com"
__status__ = "Released"

# class representing node object in Way object 
class SpeedLimitRegulatory:
    def __init__(self, relation_id, lanelet_id, limit):
        self.id = relation_id
        self.lanelet_id = lanelet_id
        self.limit = limit

    def create_xml_speed_limit_regulatory_object(self):
        relation_element = xml.Element("relation", {"id": self.id, "version": str(1), "visible": "true"})
        xml.SubElement(relation_element, "member", {"ref": self.lanelet_id, "type": "relation"})
        xml.SubElement(relation_element, "tag", {"k": "type", "v": "regulatory_element"})
        xml.SubElement(relation_element, "tag", {"k": "subtype", "v": "digital_speed_limit"})
        xml.SubElement(relation_element, "tag", {"k": "participant:vehicle", "v": "yes"})
        xml.SubElement(relation_element, "tag", {"k": "limit", "v": self.limit})
        return relation_element