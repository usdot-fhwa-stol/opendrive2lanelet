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
        fn.replace(".xodr","")

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
        fh.close()

        dom = pxml.parse(fn)
        pretty_xml_as_string = dom.toprettyxml()
        fn.replace(".osm","")

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

    def calc_distance_node_tresh(self,n1,n2):
        if(abs(n1.lat - n2.lat) < 0.000000001 and abs(n1.lon - n2.lon) < 0.000000001):
            return True
        else:
            return False
    
    def calc_distance_node_isclose(self,n1,n2):
        if(math.isclose(n1.lat, n2.lat, rel_tol=1e-10) and math.isclose(n1.lon, n2.lon, rel_tol=1e-10)):
            return True
        else:
            return False

    # apply convert_vertice_to_node to a list of nodes
    # bound_id 0,1 for left and right 
    def process_vertices(self, vertices, relation_id, bound_id):
        nodes = []
        for j in range(len(vertices)):
            node_id = relation_id + str(bound_id) + "{0:0=3d}".format(j)
            node = self.convert_vertice_to_node(node_id, vertices[j])

            duplicate_flag = False
            for i in range(len(self.all_nodes)):
                if(self.calc_distance_node_tresh(node,self.all_nodes[i])):
                    nodes.append(self.all_nodes[i])
                    duplicate_flag = True
                    break

                if(self.calc_distance_node_isclose(node,self.all_nodes[i])):
                    nodes.append(self.all_nodes[i])
                    duplicate_flag = True
                    break

            if(duplicate_flag==False):
                nodes.append(node)
                self.nodes.append(node.create_xml_node_object())
                self.all_nodes.append(node)
        return nodes
    
    def area_between_curve(self,c1,c2):

        c1_fit = np.polyfit(c1[0],c1[1],4)
        c2_fit = np.polyfit(c2[0],c2[1],4)

        c1_1d_fun = np.poly1d(c1_fit)
        c2_1d_fun = np.poly1d(c2_fit)
        
        n = np.polyint((c2_1d_fun - c1_1d_fun))
        return n

    def check_way_duplication(self,nodes,way):
        for k in self.all_ways:
            test_x = [j.local_x for j in k.nodes]
            test_y = [j.local_y for j in k.nodes]
            x = [j.local_x for j in nodes]
            y = [j.local_y for j in nodes]

            n1 = self.area_between_curve((x,y),(test_x,test_y))

            if(abs(n1(1)) < 1):
                return k
        return way

    def convert(self, fn):
        # count = 200
        c = [104, 107]
        print(self.scenario._id_set)
        print(self.scenario._lanelet_network._lanelets[104]._left_vertices)
        print(self.scenario._lanelet_network._lanelets[104]._right_vertices)

        for i in self.scenario._id_set:
        # for i in c:
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
           
            left_way = self.check_way_duplication(left_nodes,left_way)
            right_way = self.check_way_duplication(right_nodes,right_way)

            self.all_ways.append(left_way)
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
            # count = count - 1
        self.write_xml_to_file(fn)
