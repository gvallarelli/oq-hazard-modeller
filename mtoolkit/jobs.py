# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010-2011, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with OpenQuake. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
The purpose of this module is to provide functions
which tackle specific job.
"""

import logging
import numpy as np
from shapely.geometry       import Point, Polygon

from mtoolkit.eqcatalog     import EqEntryReader
from mtoolkit.smodel        import NRMLReader
from mtoolkit.utils         import get_data_path, SCHEMA_DIR

NRML_SCHEMA_PATH = get_data_path('nrml.xsd', SCHEMA_DIR)
CATALOG_MATRIX_YEAR_INDEX = 0
CATALOG_MATRIX_MW_INDEX = 5


def logged_job(job):
    """
    Decorate a job by adding logging
    statements before and after the execution
    of the job
    """

    def wrapper(context):
        """Wraps a job, adding logging statements"""
        logger = logging.getLogger('mt_logger')
        start_job_line = 'Start:\t%21s \t' % job.__name__
        end_job_line = 'End:\t%21s \t' % job.__name__
        logger.info(start_job_line)
        job(context)
        logger.info(end_job_line)
    return wrapper


@logged_job
def read_eq_catalog(context):
    """Create eq entries by reading an eq catalog"""

    reader = EqEntryReader(context.config['eq_catalog_file'])
    eq_entries = []
    for eq_entry in reader.read():
        eq_entries.append(eq_entry)
    context.eq_catalog = eq_entries


@logged_job
def read_source_model(context):
    """Create smodel definitions by reading a source model"""

    reader = NRMLReader(context.config['source_model_file'],
            NRML_SCHEMA_PATH)
    sm_definitions = []
    for sm in reader.read():
        sm_definitions.append(sm)
    context.sm_definitions = sm_definitions


@logged_job
def create_catalog_matrix(context):
    """Create a numpy matrix according to fixed attributes"""

    matrix = []
    attributes = ['year', 'month', 'day', 'longitude', 'latitude', 'Mw']
    for eq_entry in context.eq_catalog:
        matrix.append([eq_entry[attribute] for attribute in attributes])
    context.catalog_matrix = np.array(matrix)


@logged_job
def create_default_values(context):
    """
    Create default values for attributes to be used in different
    kinds of workflows
    """
    context.flag_vector = np.zeros(len(context.catalog_matrix))
    min_year = context.catalog_matrix[:, CATALOG_MATRIX_YEAR_INDEX].min()
    min_magnitude = context.catalog_matrix[:, CATALOG_MATRIX_MW_INDEX].min()
    context.completeness_table = np.array([[min_year, min_magnitude]])


@logged_job
def gardner_knopoff(context):
    """Apply gardner_knopoff declustering algorithm to the eq catalog"""

    vcl, vmain_shock, flag_vector = context.map_sc['gardner_knopoff'](
            context.catalog_matrix,
            context.config['GardnerKnopoff']['time_dist_windows'],
            context.config['GardnerKnopoff']['foreshock_time_window'])

    context.vcl = vcl
    context.catalog_matrix = vmain_shock
    context.flag_vector = flag_vector


@logged_job
def stepp(context):
    """
    Apply step algorithm to the eq catalog
    or to the numpy array built by a
    declustering algorithm
    """

    context.completeness_table = context.map_sc['stepp'](
        context.catalog_matrix[:, CATALOG_MATRIX_YEAR_INDEX],
        context.catalog_matrix[:, CATALOG_MATRIX_MW_INDEX],
        context.config['Stepp']['magnitude_windows'],
        context.config['Stepp']['time_window'],
        context.config['Stepp']['sensitivity'],
        context.config['Stepp']['increment_lock'])


def _processing_steps_required(context):
    """Return bool which states if processing steps are required"""

    return context.config['apply_processing_jobs']


class SourceModelCatalogFilter(object):

    def __init__(self, sm_filter=None):
        self.sm_filter = sm_filter
        if sm_filter is None:
            self.sm_filter = AreaSourceCatalogFilter()

    def filter_eqs(self, sm_definitions, eq_catalog):
        for sm in sm_definitions:
            yield sm, self.sm_filter.filter_eqs(sm, eq_catalog)


class AreaSourceCatalogFilter(object):
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

        polygon = self._extract_polygon(source)
        self._check_polygon(polygon)
        filtered_eq = []

        for eq in eq_catalog:
            eq_point = Point(eq[self.POINT_LONGITUDE_INDEX],
                    eq[self.POINT_LATITUDE_INDEX])

            if polygon.contains(eq_point):
                filtered_eq.append(eq)
        return np.array(filtered_eq)

    def _check_polygon(self, polygon):
        """
        Check polygon validity
        """

        if not polygon.is_valid:
            raise RuntimeError('Polygon invalid wkt: %s' % polygon.wkt)

    def _extract_polygon(self, source_model):
        """
        Create polygon using geomtry data
        defined in the source model area boundary
        """

        area_boundary = source_model['area_boundary']

        points = [(area_boundary[i], area_boundary[i + 1])
            for i in xrange(0, len(area_boundary), 2)]

        return Polygon(points)


@logged_job
def recurrence(context):
    """
    Apply recurrence algorithm to the filtered catalog
    matrix and completeness table
    """

    bval, sigb, a_m, siga_m = \
        context.map_sc['recurrence'](
            context.current_filtered_eq[:, CATALOG_MATRIX_YEAR_INDEX],
            context.current_filtered_eq[:, CATALOG_MATRIX_MW_INDEX],
            context.completeness_table,
            context.config['Recurrence']['magnitude_window'],
            context.config['Recurrence']['recurrence_algorithm'],
            context.config['Recurrence']['reference_magnitude'],
            context.config['Recurrence']['time_window'])

    context.current_sm['rupture_rate_model'][0]['a_value_cumulative'] = a_m
    context.current_sm['rupture_rate_model'][0]['b_value'] = bval
    context.current_sm['rupture_rate_model'][0]['min_magnitude'] = \
        context.config['Recurrence']['reference_magnitude']
    context.current_sm['Recurrence_sigb'] = sigb
    context.current_sm['Recurrence_siga_m'] = siga_m
