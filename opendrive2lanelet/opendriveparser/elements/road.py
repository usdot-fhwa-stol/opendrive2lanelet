
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

from opendrive2lanelet.opendriveparser.elements.roadPlanView import PlanView
from opendrive2lanelet.opendriveparser.elements.roadLink import Link
from opendrive2lanelet.opendriveparser.elements.roadLanes import Lanes
from opendrive2lanelet.opendriveparser.elements.roadElevationProfile import (
    ElevationProfile,
)
from opendrive2lanelet.opendriveparser.elements.roadLateralProfile import LateralProfile
from opendrive2lanelet.opendriveparser.elements.junction import Junction


class Road:
    """ """

    def __init__(self):
        self._id = None
        self._name = None
        self._junction = None
        self._length = None

        self._header = None  # TODO
        self._link = Link()
        self._types = []
        self._planView = PlanView()
        self._elevationProfile = ElevationProfile()
        self._lateralProfile = LateralProfile()
        self._lanes = Lanes()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def id(self):
        """ """
        return self._id

    @id.setter
    def id(self, value):
        """

        Args:
          value:

        Returns:

        """
        self._id = int(value)

    @property
    def name(self):
        """ """
        return self._name

    @name.setter
    def name(self, value):
        """

        Args:
          value:

        Returns:

        """
        self._name = str(value)

    @property
    def junction(self):
        """ """
        return self._junction

    @junction.setter
    def junction(self, value):
        """

        Args:
          value:

        Returns:

        """
        if not isinstance(value, Junction) and value is not None:
            raise TypeError("Property must be a Junction or NoneType")

        if value == -1:
            value = None

        self._junction = value

    @property
    def link(self):
        """ """
        return self._link

    @property
    def types(self):
        """ """
        return self._types

    @property
    def planView(self):
        """ """
        return self._planView

    @property
    def elevationProfile(self):
        """ """
        return self._elevationProfile

    @property
    def lateralProfile(self):
        """ """
        return self._lateralProfile

    @property
    def lanes(self):
        """ """
        return self._lanes
