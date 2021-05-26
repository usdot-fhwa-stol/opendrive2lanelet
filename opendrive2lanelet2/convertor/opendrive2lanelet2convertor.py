#!/usr/bin/env python3

# Copyright (C) 2020-2021 LEIDOS.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# -*- coding: utf-8 -*-

import os
import sys, getopt
import numpy as np
import math

from lmfit import Model
from scipy.optimize import curve_fit
from pyproj import Proj, transform
from numpy import exp, loadtxt, pi, sqrt

import xml.dom.minidom as pxml
import xml.etree.ElementTree as xml
import re
from lxml import etree

from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network
from opendrive2lanelet.osm.lanelet2osm import L2OSMConverter

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "carma@dot.gov"
__status__ = "Released"

# class used to convert opendrive map to lanelet2 map
class Opendrive2Lanelet2Convertor:
    def __init__(self, path):
        self.input_file_path = path

    def convert(self, output_file_path):
        # Open File
        file_in = open(self.input_file_path.format(os.path.dirname(os.path.realpath(__file__))), "r")
        
        # Parse XML
        tree = etree.parse(file_in)
        root = tree.getroot()
        open_drive = parse_opendrive(root)

        # Access
        header = root.find('header')
        geoReference = header.find('geoReference').text

        # Build CommonRoad Lanelet1 network
        road_network = Network()
        road_network.load_opendrive(open_drive)

        simple_geoReference = geoReference

        print('Found geoReference: ' + simple_geoReference)

        if '+geoidgrids=' in simple_geoReference:
            print('Ignoring +geoidgrids in projection as it is not currently supported')
            geoidgrids_tag = re.search('.*?(\+geoidgrids\=.*?\ +).*$', simple_geoReference).group(1)
            simple_geoReference = simple_geoReference.replace(geoidgrids_tag, '')
            print('Used conversion projection is ' + simple_geoReference)

        file_in.close()

        # Convert to Lanelet2 OSM
        osm_converter = L2OSMConverter(simple_geoReference)
        
        osm_map = osm_converter(road_network.export_commonroad_scenario())

        # Add georeference back to osm
        geo_tag = etree.Element('geoReference')
        geo_tag.text = geoReference
        osm_map.insert(0, geo_tag)

        with open(output_file_path, "wb") as file_out:
            file_out.write(
                etree.tostring(
                    osm_map, xml_declaration=True, encoding="UTF-8", pretty_print=True
                )
            )
