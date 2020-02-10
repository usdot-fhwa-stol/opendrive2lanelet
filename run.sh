#!/bin/bash
FILES=/root/opendrive2lanelet/map/*.xodr
for i in $FILES
do
  echo "Start Processing $i file"
  python opendrive2lanelet2convertor.py -i $i -o "$i.osm"
  cp "$i.osm" /root/output/
  echo "Finished Processing $i !"
done