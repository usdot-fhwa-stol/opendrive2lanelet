#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import xml.etree.ElementTree as xml

__author__ = "Samir Tabriz"
__version__ = "1.0.0"
__maintainer__ = "Samir Tabriz"
__email__ = "samir.manafzadehtabriz@leidos.com"
__status__ = "Released"

# class representing relation in lanelet2
class Relation:
    def __init__(self, id, member_left, member_right, from_cad_id, to_cad_id, cad_id, relation_type):
        self.id = str(id)
        self.member_left = member_left
        self.member_right = member_right
        self.member_left_id = str(member_left.id)
        self.member_right_id = str(member_right.id)
        self.from_cad_id = from_cad_id
        self.to_cad_id = to_cad_id
        self.relation_type = relation_type
        self.cad_id = cad_id
        self.turn_direction = "straight"
        self.set_turn_direction()

    def create_xml_relation_object(self):
        relation_element = xml.Element("relation", {"id": self.id, "version": str(1), "visible": "true"})
        xml.SubElement(relation_element, "member", {"ref": self.member_left_id, "role": str("left"), "type": "way"})
        xml.SubElement(relation_element, "member", {"ref": self.member_right_id, "role": str("right"), "type": "way"})
        xml.SubElement(relation_element, "tag", {"k": "cad_id", "v": self.cad_id})
        xml.SubElement(relation_element, "tag", {"k": "direction", "v": "ONE_WAY"})
        xml.SubElement(relation_element, "tag", {"k": "level", "v": "0"})
        xml.SubElement(relation_element, "tag", {"k": "location", "v": "private"})
        xml.SubElement(relation_element, "tag", {"k": "participant:vehicle", "v": "yes"})
        xml.SubElement(relation_element, "tag", {"k": "road_type", "v": "road"})
        xml.SubElement(relation_element, "tag", {"k": "subtype", "v": "road"})
        xml.SubElement(relation_element, "tag", {"k": "type", "v": "lanelet"})
        xml.SubElement(relation_element, "tag", {"k": "from_cad_id", "v": self.from_cad_id})
        xml.SubElement(relation_element, "tag", {"k": "to_cad_id", "v": self.to_cad_id})
        xml.SubElement(relation_element, "tag", {"k": "near_spaces", "v": "[]"})
        xml.SubElement(relation_element, "tag", {"k": "turn_direction", "v": self.turn_direction})
        return relation_element

    # start is the first point of lanelet
    # mid is the secound point of lanlelet
    # end is the last point of lanelet
    # set_direction is used by set_turn direction to check if the lanelet is turning left or right
    def set_direction(self, start, mid, end):
        if(((mid[0] - start[0])*(end[1] - start[1]) - (mid[1] - start[1])*(end[0] - start[0])) > 0):
            return 1
        else:
            return 0

    #set_turn_direction is used to set set the turn_direction tag in lanelet
    def set_turn_direction(self):
        turn_direction = "straight"
        if(len(self.from_cad_id) == 1 and len(self.to_cad_id) == 1):
            start = np.array([self.member_left.nodes[0].local_x,self.member_left.nodes[0].local_y])
            mid = np.array([self.member_left.nodes[1].local_x,self.member_left.nodes[1].local_y])
            end = np.array([self.member_left.nodes[-1].local_x,self.member_left.nodes[-1].local_y])

            start_mid = mid - start
            start_end = end - start
            cosine_angle = np.dot(start_mid, start_end) / (np.linalg.norm(start_mid) * np.linalg.norm(start_end))
            alpha = np.arccos(cosine_angle)

            if(np.degrees(alpha) > 10):
                if(self.set_direction(start,mid,end) == 0):
                    turn_direction = "right"
                else:
                    turn_direction = "left"

        self.turn_direction = turn_direction
