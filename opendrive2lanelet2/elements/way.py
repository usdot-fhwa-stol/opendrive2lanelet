#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xml

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "samir.manafzadehtabriz@leidos.com"
__status__ = "Released"

# class representing Way object in Relation object members
class Way:
    def __init__(self, id, nodes, max_speed):
        self.id = id
        self.nodes = nodes
        # self.max_speed = max_speed
    
    def create_xml_way_object(self):
        way_element = xml.Element("way", {"id": self.id, "version": str(1), "visible": "true"})
        for i in self.nodes:
            xml.SubElement(way_element, "nd", {"ref": str(i.id)})
        xml.SubElement(way_element, "tag", {"k": "type", "v": "line_thin"})
        xml.SubElement(way_element, "tag", {"k": "subtype", "v": "solid"})
        # xml.SubElement(way_element, "tag", {"k": "maxspeed", "v": str(self.max_speed)})
        return way_element
