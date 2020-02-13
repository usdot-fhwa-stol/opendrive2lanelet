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

import xml.etree.ElementTree as xml
from lxml import etree

from opendrive2lanelet.opendriveparser.parser import parse_opendrive
from opendrive2lanelet.network import Network
from opendrive2lanelet2.elements.node import Node
from opendrive2lanelet2.elements.way import Way
from opendrive2lanelet2.elements.relation import Relation

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

        self.root.append(xml.Element('geoReference', {'v': self.geoReference}))

        for child in self.nodes.getchildren():
            self.root.append(child)

        for child in self.ways.getchildren():
            self.root.append(child)

        for child in self.relations.getchildren():
            self.root.append(child)

        tree = xml.ElementTree(self.root)
        fh = open(fn, "wb")
        tree.write(fh)
    
    # convert vertice from opendrive to a node in lanelet 
    def convert_vertice_to_node(self,node_id,vertice):
        x = vertice[0]
        y = vertice[1]
        lon, lat = self.get_point_geo(x,y)
        local_x, local_y = x, y
        return Node(node_id,lat,lon, local_x, local_y)
    
    # apply convert_vertice_to_node to a list of nodes
    # bound_id 0,1 for left and right 
    def process_vertices(self, vertices, relation_id, bound_id):
        nodes = []
        for j in range(len(vertices)):
            node_id = relation_id + str(bound_id) + "{0:0=3d}".format(j)
            node = self.convert_vertice_to_node(node_id, vertices[j])

            duplicate_flag = False
            for i in range(len(self.all_nodes)):
                if(abs(node.lat - self.all_nodes[i].lat) < 0.000000001 and abs(node.lon - self.all_nodes[i].lon) < 0.000000001):
                    nodes.append(self.all_nodes[i])
                    duplicate_flag = True
                    break

                if(math.isclose(node.lat, self.all_nodes[i].lat, rel_tol=1e-10) and math.isclose(node.lon, self.all_nodes[i].lon, rel_tol=1e-10)):
                    nodes.append(self.all_nodes[i])
                    duplicate_flag = True
                    break

            if(duplicate_flag==False):
                nodes.append(node)
                self.nodes.append(node.create_xml_node_object())
                self.all_nodes.append(node)
        return nodes

    def convert(self, fn):
        # count = 200
        # c = [140, 135, 107]
        for i in self.scenario._id_set:
            # if(count > 0):
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

            for k in self.all_ways:
                test_x = [j.local_x for j in k.nodes]
                test_y = [j.local_y for j in k.nodes]
                x = [j.local_x for j in left_nodes]
                y = [j.local_y for j in left_nodes]

                z = np.polyfit(x,y,3)
                z_test = np.polyfit(test_x,test_y,3)

                f = np.poly1d(z)
                f_test = np.poly1d(z_test)
                
                n = np.polyint((f_test - f))

                if(abs(n(1)) < 1):
                    left_way = k

            for k in self.all_ways:
                test_x = [j.local_x for j in k.nodes]
                test_y = [j.local_y for j in k.nodes]
                x = [j.local_x for j in right_nodes]
                y = [j.local_y for j in right_nodes]

                z = np.polyfit(x,y,3)
                z_test = np.polyfit(test_x,test_y,3)

                f = np.poly1d(z)
                f_test = np.poly1d(z_test)
                
                n = np.polyint((f_test - f))

                if(abs(n(1)) < 1):
                    right_way = k

            self.all_ways.append(left_way)
            self.all_ways.append(right_way)

            self.ways.append(left_way.create_xml_way_object())
            self.ways.append(right_way.create_xml_way_object())

            from_cad_id = self.scenario._lanelet_network._lanelets[i]._successor
            to_cad_id = self.scenario._lanelet_network._lanelets[i]._predecessor
            relation = Relation(relation_id, left_way, right_way, from_cad_id, to_cad_id, cad_id, "lanelet")
            self.relations.append(relation.create_xml_relation_object())
            # count = count - 1

        self.write_xml_to_file(fn)
