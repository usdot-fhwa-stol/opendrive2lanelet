#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xml

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "samir.manafzadehtabriz@leidos.com"
__status__ = "Released"

# class representing node object in Way object 
class Node:
    def __init__(self, id, lat, lon, local_x, local_y):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.local_x = local_x
        self.local_y = local_y

    def create_xml_node_object(self):
        node_element = xml.Element('node',{'id': str(self.id), 'lat': str(self.lat), 'lon': str(self.lon), 'version': str(1), 'visible': 'true'})
        xml.SubElement(node_element, "tag", {"k": "ele", "v": "0.0"})
        return node_element
