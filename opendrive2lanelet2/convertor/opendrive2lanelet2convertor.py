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
from opendrive2lanelet2.elements.node import Node
from opendrive2lanelet2.elements.way import Way
from opendrive2lanelet2.elements.relation import Relation
from opendrive2lanelet2.elements.speed_limit_regulatory import SpeedLimitRegulatory

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "samir.manafzadehtabriz@leidos.com"
__status__ = "Released"

# class used to convert opendrive map to lanelet2 map
class Opendrive2Lanelet2Convertor:
    def __init__(self, fn):
        self.scenario, self.geoReference = self.open_drive_loader(fn)
        self.root = xml.Element('osm',{'generator': 'lanelet2','version': '0.6'})
        self.nodes = xml.Element('nodes')
        self.ways = xml.Element('ways')
        self.relations = xml.Element('relations')
        self.all_nodes = []
        self.all_nodes_dict = dict()
        self.all_ways = []

    def open_drive_loader(self, fn):
        fi = open(fn.format(os.path.dirname(os.path.realpath(__file__))), "r")
        tree = etree.parse(fi)
        root = tree.getroot()
        geoReference = root[0][0].text
        open_drive = parse_opendrive(root)
        road_network = Network()
        road_network.load_opendrive(open_drive)
        return road_network.export_commonroad_scenario(), geoReference

    # convert x,y values to geo points using the geo reference defined in the input file
    def get_point_geo(self,x,y):
        inProj = Proj(self.geoReference)
        return inProj(x,y,inverse=True)

    def write_xml_to_file(self,fn):
        fn = fn.replace(".xodr","")

        geo_reference = xml.Element('geoReference')
        geo_reference.text = self.geoReference
        self.root.append(geo_reference)

        for child in self.nodes.getchildren():
            self.root.append(child)

        for child in self.ways.getchildren():
            self.root.append(child)

        for child in self.relations.getchildren():
            self.root.append(child)

        tree = xml.ElementTree(self.root)
        fh = open(fn, "wb")
        tree.write(fh)
        fh.close()

        dom = pxml.parse(fn)
        pretty_xml_as_string = dom.toprettyxml()
        fn = fn.replace(".osm","")

        fh = open(fn + "_pretty.osm", "w+")
        fh.write(pretty_xml_as_string)
        fh.close()

    # convert vertice from opendrive to a node in lanelet 
    def convert_vertice_to_node(self,node_id,vertice):
        x = vertice[0]
        y = vertice[1]
        lon, lat = self.get_point_geo(x,y)
        local_x, local_y = x, y
        return Node(node_id,lat,lon, local_x, local_y)

    # The key for the dictionary will be of the form: 'lat_lon',
    # where lat and lon are integers (lat here = input latitude / threshold) ,
    # and each have 12 number slots associated.
    # This number is set for the current threshold of 0.00000001,
    # where the maximum longitude value of -180 turns into: -18000000000,
    # filling up all 12 slots. ex: for the point [179.992125274, -45.12893761],
    # the key is: '017999212527_-04512893761'
    def key_from_latlon_prec(self, point):
        return f'{int(np.round(point[0],0)):012d}' + '_' + f'{int(np.round(point[1],0)):012d}'


    # Uses a dictionary, self.all_nodes_dict, which contains key-value pairs for all existing points
    # If there is an existing point within the threshold distance, it returns True and the index of that point
    # If not, it adds the point to the dictionary and returns False
    def check_duplicate_hash_precise(self, new, tolerace=0.00000001):
        # Grab 5 relative points {-1.1, -0.5, 0, 0.5, 1} in both latitude and longitude
        new = new / tolerace
        thresh_range = [-1.1, -0.5, 0, 0.5, 1.1]
        for lat_threshold in thresh_range:
            for lon_threshold in thresh_range:
                threshold = np.array([lat_threshold, lon_threshold])
                test = new + np.round(threshold, 8)

                # The float -> int conversion will fail if the input value is infinite: float('inf')
                # If that happens, asssume that it isn't a duplicate and return that is isn't a duplicate
                try:
                    test_key = self.key_from_latlon_prec(test)
                except OverflowError:
                    print('Lat or lon over max value')
                    return False, None

                if test_key in self.all_nodes_dict:
                    [point, value] = self.all_nodes_dict[test_key]
                    difference = np.abs(point - new)
                    if difference[0] < 1 and difference[1] < 1:
                        return True, value
        test_key = self.key_from_latlon_prec(new)
        value = len(self.all_nodes_dict)
        self.all_nodes_dict[test_key] = [new, value]
        return False, None

    # apply convert_vertice_to_node to a list of nodes
    # bound_id 0,1 for left and right 
    def process_vertices(self, vertices, relation_id, bound_id):
        nodes = []
        for j in range(len(vertices)):
            node_id = relation_id + str(bound_id) + "{0:0=3d}".format(j)
            node = self.convert_vertice_to_node(node_id, vertices[j])
            node_latlon = np.array([node.lat, node.lon])

            is_dup, index = self.check_duplicate_hash_precise(node_latlon)
            if is_dup:
                nodes.append(self.all_nodes[index])
            else:
                nodes.append(node)
                self.nodes.append(node.create_xml_node_object())
                self.all_nodes.append(node)

        return nodes

    # check for way duplication in the entire map
    def check_way_duplication(self,nodes,way):
    # For a duplicate, need at least 5, and at least 80% matching points
        intersection_test_tresh = 5
        intersection_test_tresh_ratio = 0.8

        for k in self.all_ways:
            # Get list of points in existing and candidate ways
            test_pts = np.array([[np.round(j.local_x, 3), np.round(j.local_y, 3)] for j in k.nodes])
            pts = np.array([[np.round(j.local_x, 3), np.round(j.local_y, 3)] for j in nodes])

            # Count the number and ratio of duplicate points
            combined = np.concatenate((test_pts, pts))
            tmp, indices = np.unique(combined, axis=0, return_index=True)
            num_matches = np.shape(combined)[0] - len(indices)
            ratio_matches = 2 * num_matches / np.shape(combined)[0]

            # If the ratio and count tests pass, re-use the esisting way
            if num_matches > intersection_test_tresh:
                if ratio_matches > intersection_test_tresh_ratio:
                    return k
        return way

    def convert(self, fn):
        for i in self.scenario._id_set:
            left_nodes = []
            right_nodes = []
            relation_id = str(i)
            cad_id = str(i)

            left_nodes = self.process_vertices(self.scenario._lanelet_network._lanelets[i]._left_vertices, relation_id, 0)
            right_nodes = self.process_vertices(self.scenario._lanelet_network._lanelets[i]._right_vertices, relation_id, 1)

            max_speed = self.scenario._lanelet_network._lanelets[i]._speed_limit

            left_way_id = relation_id + '0'
            left_way = Way(left_way_id,left_nodes, max_speed)

            right_way_id = relation_id + '1'
            right_way = Way(right_way_id,right_nodes, max_speed)

            left_way = self.check_way_duplication(left_nodes,left_way)
            self.all_ways.append(left_way)

            right_way = self.check_way_duplication(right_nodes,right_way)
            self.all_ways.append(right_way)

            self.ways.append(left_way.create_xml_way_object())
            self.ways.append(right_way.create_xml_way_object())

            from_cad_id = self.scenario._lanelet_network._lanelets[i]._successor
            to_cad_id = self.scenario._lanelet_network._lanelets[i]._predecessor

            speed_limit_regulatory_id = relation_id +'00'
            speed_limit_regulatory = SpeedLimitRegulatory(speed_limit_regulatory_id, relation_id, str(max_speed))

            relation = Relation(relation_id, left_way, right_way, from_cad_id, to_cad_id, cad_id, "lanelet",speed_limit_regulatory_id)

            self.relations.append(relation.create_xml_relation_object())
            self.relations.append(speed_limit_regulatory.create_xml_speed_limit_regulatory_object())

        self.write_xml_to_file(fn)