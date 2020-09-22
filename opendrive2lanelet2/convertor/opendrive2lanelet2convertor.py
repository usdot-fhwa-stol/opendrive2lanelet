#!/usr/bin/env python
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
        geoReference = root[0][0].text

        # Build CommonRoad Lanelet1 network
        road_network = Network()
        road_network.load_opendrive(open_drive)

        # Convert to Lanelet2 OSM
        osm_converter = L2OSMConverter(geoReference)
        
        file_in.close()

        # Write OSM file
        osm_map = osm_converter(road_network.export_commonroad_scenario())
        with open(output_file_path, "wb") as file_out:
            file_out.write(
                etree.tostring(
                    osm_map, xml_declaration=True, encoding="UTF-8", pretty_print=True
                )
            )