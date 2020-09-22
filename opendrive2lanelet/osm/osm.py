"""Module for OSM representation in python."""

__author__ = "Benjamin Orthen"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ["Priority Program SPP 1835 Cooperative Interacting Automobiles"]
__version__ = "1.1.2"
__maintainer__ = "Benjamin Orthen"
__email__ = "commonroad-i06@in.tum.de"
__status__ = "Released"


from lxml import etree

DEFAULT_PROJ_STRING = "+proj=utm +zone=32 +ellps=WGS84"


class Node:
    """OSM Node."""

    def __init__(self, id_, lat, lon):
        self.id_ = str(id_)
        self.lat = str(lat)
        self.lon = str(lon)

    def serialize_to_xml(self):
        node = etree.Element("node")
        node.set("id", self.id_)
        node.set("action", "modify")
        node.set("visible", "true")
        node.set("version", "1")
        node.set("lat", self.lat)
        node.set("lon", self.lon)

        return node


class Way:
    """OSM Way."""

    def __init__(self, id_: str, *nodes):
        self.id_ = str(id_)
        self.nodes = []
        self.type = "line_thin"
        self.subtype = "solid"

        for node in nodes:
            self.nodes.append(node)

    def serialize_to_xml(self):
        way = etree.Element("way")
        way.set("id", self.id_)
        way.set("action", "modify")
        way.set("visible", "true")
        way.set("version", "1")

        type_tag = etree.SubElement(way, "tag")
        type_tag.set("k", "type")
        type_tag.set("v",  self.type)

        subtype_tag = etree.SubElement(way, "tag")
        subtype_tag.set("k", "subtype")
        subtype_tag.set("v",  self.subtype)

        for node in self.nodes:
            xml_node = etree.SubElement(way, "nd")
            xml_node.set("ref", node)

        return way

class DigitalSpeedLimitReg:
    """DigitalSpeedLimitRegulation"""

    def __init__(self, id_: str, lanelet, way_relation_id):
        self.id_ = str(id_)
        self.type = "regulatory_element"
        self.subtype = "digital_speed_limit"
        self.particpants = ["participant:vehicle"]
        self.limit = str(lanelet.speed_limit) + " mph"
        self.lanelet = lanelet
        self.way_relation_id = way_relation_id

    def serialize_to_xml(self):
        reg = etree.Element("relation")
        reg.set("id", self.id_)
        reg.set("action", "modify")
        reg.set("visible", "true")
        reg.set("version", "1")

        type_tag = etree.SubElement(reg, "tag")
        type_tag.set("k", "type")
        type_tag.set("v",  self.type)

        subtype_tag = etree.SubElement(reg, "tag")
        subtype_tag.set("k", "subtype")
        subtype_tag.set("v",  self.subtype)

        limit_tag = etree.SubElement(reg, "tag")
        limit_tag.set("k", "limit")
        limit_tag.set("v",  self.limit)
        
        for participant in self.particpants:
            participant_tag = etree.SubElement(reg, "tag")
            participant_tag.set("k", participant)
            participant_tag.set("v", "yes")

        refers = etree.SubElement(reg, "member")
        refers.set("type", "relation")
        refers.set("ref", str(self.way_relation_id))
        refers.set("role", "refers")

        return reg


class WayRelation:
    """Relation for a lanelet with a left and a right way."""

    def __init__(self, id_: str, left_way: Way, right_way: Way, speed_limit_id, turn_direction = "straight"):
        self.id_ = str(id_)
        self.left_way = left_way
        self.right_way = right_way
        self.speed_limit_id = speed_limit_id
        self.location = "urban"
        self.turn_direction = turn_direction
        self.subtype = "road"

    def serialize_to_xml(self) -> etree.Element:
        rel = etree.Element("relation")
        rel.set("id", self.id_)
        rel.set("action", "modify")
        rel.set("visible", "true")
        rel.set("version", "1")

        right_way = etree.SubElement(rel, "member")
        right_way.set("type", "way")
        right_way.set("ref", self.right_way)
        right_way.set("role", "right")
        left_way = etree.SubElement(rel, "member")
        left_way.set("type", "way")
        left_way.set("ref", self.left_way)
        left_way.set("role", "left")
        tag = etree.SubElement(rel, "tag")
        tag.set("k", "type")
        tag.set("v", "lanelet")

        subtype_tag = etree.SubElement(rel, "tag")
        subtype_tag.set("k", "subtype")
        subtype_tag.set("v", self.subtype)

        speed_limit = etree.SubElement(rel, "member")
        speed_limit.set("type", "relation")
        speed_limit.set("ref", self.speed_limit_id)
        speed_limit.set("role", "regulatory_element")

        loc_tag = etree.SubElement(rel, "tag")
        loc_tag.set("k", "location")
        loc_tag.set("v",  self.location)

        turn_tag = etree.SubElement(rel, "tag")
        turn_tag.set("k", "turn_direction")
        turn_tag.set("v",  self.turn_direction)

        return rel

class OSM:
    """Basic OSM representation."""

    def __init__(self):
        self.nodes = []
        self._ways = []
        self.way_relations = []
        self.digital_speed_limit_regulations = []

    def add_node(self, node: Node):
        """Add a new node to the OSM.

        Args:
          node: Node to be added.
        """
        self.nodes.append(node)

    def add_way(self, way: Way):
        self._ways.append(way)

    def add_way_relation(self, way_relation: WayRelation):
        self.way_relations.append(way_relation)

    def add_digital_speed_limit(self, speed_limit_reg: DigitalSpeedLimitReg):
        self.digital_speed_limit_regulations.append(speed_limit_reg)

    def find_way_by_id(self, way_id: str) -> Way:
        for way in self._ways:
            if way.id_ == way_id:
                return way
        return None

    def find_node_by_id(self, node_id: str) -> Node:
        for nd in self.nodes:
            if nd.id_ == node_id:
                return nd

        return None

    def find_way_rel_by_id(self, way_rel_id: str) -> WayRelation:
        """Find and return the WayRelation of the OSM if it matches the id.

        Args:
          way_rel_id: Id to be matched.
        """
        for wr in self.way_relations:
            if wr.id_ == way_rel_id:
                return wr

        return None

    def serialize_to_xml(self) -> etree.Element:
        """Serialize the OSM to an XML document."""
        osm = etree.Element("osm")
        osm.set("version", "0.6")
        osm.set("upload", "true")
        osm.set("generator", "opendrive2lanelet")

        for node in self.nodes:
            osm.append(node.serialize_to_xml())

        for way in self._ways:
            osm.append(way.serialize_to_xml())

        for way_relation in self.way_relations:
            osm.append(way_relation.serialize_to_xml())

        for reg in self.digital_speed_limit_regulations:
            osm.append(reg.serialize_to_xml())

        return osm
