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
from opendrive2lanelet2.convertor.opendrive2lanelet2convertor import Opendrive2Lanelet2Convertor

def main(argv):

    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('opendrive2lanelet2convertor.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('opendrive2lanelet2convertor.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    if(inputfile is not None and outputfile is not None):
        if not inputfile.endswith(".xodr"):
            print('Input file must be OpenDRIVE .xodr file')
            sys.exit()
        if not outputfile.endswith(".osm"):
            print('Output file must be Lanelet2 .osm file')
            sys.exit()
        
        open_drive2_lanelet2_convertor = Opendrive2Lanelet2Convertor(inputfile)
        open_drive2_lanelet2_convertor.convert(outputfile)

if __name__== "__main__":
    main(sys.argv[1:])