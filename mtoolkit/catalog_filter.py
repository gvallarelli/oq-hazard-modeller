# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010-2011, GEM Foundation.
#
# MToolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# MToolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with MToolkit. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
The purpose of this module is to provide objects
which apply different filtering strategies to
the earthquake catalog.
"""

from shapely.geometry import Point, Polygon
import numpy as np
import logging

LOGGER = logging.getLogger('mt_logger')


class CatalogFilter(object):
    """
    SourceModelCatalogFilter allows to filter
    out eq events within a geometry defined
    in a generic source model
    """

    def __init__(self, sm_filter=None):
        self.sm_filter = sm_filter
        if sm_filter is None:
            self.sm_filter = NullCatalogFilter()

    def filter_eqs(self, sm_definitions, eq_catalog):
        """
        Apply filtering to eq catalog
        """

        for sm in sm_definitions:
            yield sm, self.sm_filter.filter_eqs(sm, eq_catalog)


class SourceModelCatalogFilter(object):
    """
    AreaSourceCatalogFilter allows to filter
    out eq events within a geometry defined
    in an area source model
    """

    POINT_LATITUDE_INDEX = 4
    POINT_LONGITUDE_INDEX = 3

    def filter_eqs(self, source, eq_catalog):
        """
        Filter eq events contained in
        the polygon
        """

        polygon = _extract_polygon(source)
        _check_polygon(polygon)
        filtered_eq = []

        for eq in eq_catalog:
            eq_point = Point(eq[self.POINT_LONGITUDE_INDEX],
                    eq[self.POINT_LATITUDE_INDEX])

            if polygon.contains(eq_point):
                filtered_eq.append(eq)

        LOGGER.info(''.center(80, '-'))

        LOGGER.info("SOURCE MODEL GEOMETRY FILTERING")

        LOGGER.debug("Number of events inside the zone %s: %s" %
            (source.name, len(filtered_eq)))

        return np.array(filtered_eq)


def _check_polygon(polygon):
    """
    Check polygon validity
    """

    if not polygon.is_valid:
        raise RuntimeError('Polygon invalid wkt: %s' % polygon.wkt)


def _extract_polygon(source_model):
    """
    Create polygon using geomtry data
    defined in the source model area boundary
    """

    return Polygon(source_model.area_boundary.pos_list)


class NullCatalogFilter(object):
    """
    NullCatalogFilter doesn't apply any kind
    of filtering to the eq events defined in the
    catalogue
    """

    def filter_eqs(self, source, eq_catalog):
        return np.array(eq_catalog)
