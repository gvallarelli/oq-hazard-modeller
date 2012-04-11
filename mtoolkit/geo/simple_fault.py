# -*- coding: utf-8 -*-

# Copyright (c) 2010-2012, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.
"""
Module :mod:`mtoolkit.geo.simple_fault` defines :class:`SimpleFaultGeo`.
"""

from numpy import radians, sin, cos, arctan2, sqrt


def ensure(exp, msg):
    """
    Utility method that raises an error if the
    given condition is not true.
    """

    if not exp:
        raise ValueError(msg)


class SimpleFaultGeo(object):
    """
    Represents a simple fault geometry.

    :param trace:
        list of points where each point is a tuple (longitude, latitude).
    :param upp_depth:
        Upper depth represents the depth of the shallowest edge of
        the fault (km).
    :param low_depth:
        Lower depth represents the depth of the deepest edge
        of the fault (km).
    :param dip:
        The angle (in degrees) between the fault and horizontal plane.
    """

    def __init__(self, trace, upp_depth, low_depth, dip):
        for point in trace:
            ensure(-180 <= point[0] <= 180,
                'Longitude should be between -180 and 180')
            ensure(-90 <= point[1] <= 90,
                'Latitude should be between -90 and 90')
        ensure(upp_depth >= 0, 'Upper depth should be a positive float %d')
        ensure(low_depth > 0, 'Lower depth should be greater than zero')
        ensure(low_depth > upp_depth,
            'Lower depth should be greater than Upper depth')
        ensure(0 < dip <= 90,
            'Dip should be greater than zero and less or equal to 90')

        self._trace = trace
        self._upp_depth = upp_depth
        self._low_depth = low_depth
        self._dip = dip
        self._length = None
        self._width = None
        self._area = None

    def get_length(self):
        """
        Returns the length of the simple fault geometry (in km).
        """

        if self._length:
            return self._length
        self._length = self._distance()
        return self._length

    def get_width(self):
        """
        Returns the width of the simple fault geometry (in km).
        """

        if self._width:
            return self._width
        self._width = (
            (self._low_depth - self._upp_depth) / sin(radians(self._dip)))
        return self._width

    def get_area(self):
        """
        Returns the area of the simple fault geometry (in square km).
        """

        if self._area:
            return self._area
        self._area = self.get_length() * self.get_width()
        return self._area

    def _distance(self):
        """
        Calculate distance between points where distance
        is defined as the sum of distances among consecutive
        points. The distance between two points is calculated
        using the Haversine formula.
        http://en.wikipedia.org/wiki/Haversine_formula
        """

        distance = 0
        radius = 6371.0

        for i in range(len(self._trace) - 1):

            lon1 = radians(self._trace[i][0])
            lat1 = radians(self._trace[i][1])

            lon2 = radians(self._trace[i + 1][0])
            lat2 = radians(self._trace[i + 1][1])

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2.0) ** 2 + (
                (cos(lat1) * cos(lat2)) * (sin(dlon / 2.0) ** 2))

            c = 2.0 * arctan2(sqrt(a), sqrt(1.0 - a))

            d = radius * c

            distance += d

        return distance
