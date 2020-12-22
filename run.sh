#!/bin/bash

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

FILES=/root/opendrive2lanelet/map/*.xodr
for i in $FILES
do
  echo "Start Processing $i file"
  python opendrive2lanelet2convertor.py -i $i -o "$i.osm"
  echo "Finished Processing $i"
done