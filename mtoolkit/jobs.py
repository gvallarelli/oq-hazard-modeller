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
The purpose of this module is to provide functions which tackle specific job,
some of them wrap scientific functions defined in the scientific module.
"""

import logging
import numpy as np

from mtoolkit.eqcatalog import EqEntryReader, EqEntryWriter
from nrml.reader import NRMLReader
from nrml.nrml_xml import get_data_path, SCHEMA_DIR
from mtoolkit.source_model import default_area_source


NRML_SCHEMA_PATH = get_data_path('nrml.xsd', SCHEMA_DIR)
CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX = 0
CATALOG_MATRIX_MW_INDEX = 5
CATALOG_MATRIX_FIXED_COLOUMNS = ['year', 'month', 'day',
                                'longitude', 'latitude', 'Mw']
COMPLETENESS_TABLE_MW_INDEX = 1

LOGGER = logging.getLogger('mt_logger')


def logged_job(job):
    """
    Decorate a job by adding logging
    statements before and after the execution
    of the job.
    """

    def wrapper(context):
        """Wraps a job, adding logging statements"""
        LOGGER.info(''.center(80, '-'))
        LOGGER.info(" %22s " % job.__name__.upper())
        job(context)

    return wrapper


@logged_job
def read_eq_catalog(context):
    """
    Create eq entries by reading an e] catalog.
    :param context: shared datastore across different jobs
        in a pipeline
    """

    reader = EqEntryReader(context.config['eq_catalog_file'])
    eq_entries = []
    for eq_entry in reader.read():
        eq_entries.append(eq_entry)
    context.eq_catalog = eq_entries

    LOGGER.debug("* Eq catalog length: %s" % len(context.eq_catalog))


@logged_job
def read_source_model(context):
    """
    Create source model definitions by reading a source model.
    :param context: shared datastore across different jobs
        in a pipeline
    """

    sm_definitions = []

    reader = NRMLReader(context.config['source_model_file'], NRML_SCHEMA_PATH)
    for sm in reader.read():
        sm_definitions.append(sm)

        context.sm_definitions = sm_definitions

    LOGGER.debug("* Eq number source models: %s" % len(context.sm_definitions))


@logged_job
def create_default_source_model(context):
    """
    Create a default source model object
    :param context: shared datastore across different jobs
        in a pipeline
    """

    context.sm_definitions = [default_area_source()]

    LOGGER.debug("* Eq number source models: %s" % len(context.sm_definitions))


@logged_job
def create_catalog_matrix(context):
    """
    Create a numpy matrix according to fixed attributes.
    :param context: shared datastore across different jobs
        in a pipeline
    """

    matrix = []
    for eq_entry in context.eq_catalog:
        matrix.append([eq_entry[coloumn] for coloumn in
                        CATALOG_MATRIX_FIXED_COLOUMNS])

    context.catalog_matrix = np.array(matrix)
    context.working_catalog = np.array(matrix)


@logged_job
def create_default_values(context):
    """
    Create default values for context attributes to be
    used in different kinds of workflows.
    :param context: shared datastore across different jobs
        in a pipeline
    """

    context.flag_vector = np.zeros(len(context.working_catalog))
    min_year = context.working_catalog[:,
        CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX].min()
    min_magnitude = context.working_catalog[:, CATALOG_MATRIX_MW_INDEX].min()
    context.completeness_table = np.array([[min_year, min_magnitude]])


@logged_job
def gardner_knopoff(context):
    """
    Apply gardner_knopoff declustering algorithm to the eq catalog.
    :param context: shared datastore across different jobs
        in a pipeline
    """

    vcl, vmain_shock, flag_vector = context.map_sc['gardner_knopoff'](
            context.working_catalog,
            context.config['GardnerKnopoff']['time_dist_windows'],
            context.config['GardnerKnopoff']['foreshock_time_window'])

    context.vcl = vcl
    context.working_catalog = vmain_shock
    context.flag_vector = flag_vector

    LOGGER.debug(
        "* Number of events after declustering: %s" % len(vmain_shock))

    LOGGER.debug(
        "* Number of events removed during declustering: %s" %
        (np.sum(flag_vector != 0)))

    LOGGER.debug(
        "* Number of cluster identified: %s" %
        (np.size(np.unique(vcl), 0) - 1))


@logged_job
def stepp(context):
    """
    Apply step algorithm to the catalog matrix
    :param context: shared datastore across different jobs
        in a pipeline
    """

    context.completeness_table = context.map_sc['stepp'](
        context.working_catalog[:, CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX],
        context.working_catalog[:, CATALOG_MATRIX_MW_INDEX],
        context.config['Stepp']['magnitude_windows'],
        context.config['Stepp']['time_window'],
        context.config['Stepp']['sensitivity'],
        context.config['Stepp']['increment_lock'])

    LOGGER.debug(
        "* Number of events into completeness algorithm: %s"
            % len(context.working_catalog))

    LOGGER.debug(
        "* Completeness table: ")

    LOGGER.debug(context.completeness_table)


def create_selected_eq_vector(context):
    """
    Apply selected_eq_flag_vector algorithm to
    the catalog matrix and completeness table
    :param context: shared datastore across different jobs
        in a pipeline
    """

    context.selected_eq_vector = context.map_sc['select_eq_vector'](
        context.catalog_matrix[:, CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX],
        context.catalog_matrix[:, CATALOG_MATRIX_MW_INDEX],
        context.completeness_table[:, CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX],
        context.completeness_table[:, COMPLETENESS_TABLE_MW_INDEX],
        context.flag_vector)


@logged_job
def store_preprocessed_catalog(context):
    """
    Write in a csv file the earthquake
    catalog after preprocessing jobs (i.e.
    gardner_knopoff, stepp)
    """

    writer = EqEntryWriter(
        context.config['pprocessing_result_file'])
    writer_cr = writer.write_row()
    writer_cr.next()

    number_written_eq = 0
    index = 0

    for index, entry in enumerate(
        context.selected_eq_vector):
        if entry == 0:
            writer_cr.send(context.eq_catalog[index])
            number_written_eq += 1
    writer_cr.close()

    LOGGER.debug("* Stored Eq entries: %d" % number_written_eq)

    LOGGER.debug("* Number of events removed after preprocessing jobs: %d" %
        ((index + 1) - number_written_eq))


@logged_job
def recurrence(context):
    """
    Apply recurrence algorithm to the filtered catalog
    matrix and completeness table
    :param context: shared datastore across different jobs
        in a pipeline
    """

    bval, sigb, a_m, siga_m = context.map_sc['recurrence'](
            context.current_filtered_eq[:,
                CATALOG_COMPLETENESS_MATRIX_YEAR_INDEX],
            context.current_filtered_eq[:, CATALOG_MATRIX_MW_INDEX],
            context.completeness_table,
            context.config['Recurrence']['magnitude_window'],
            context.config['Recurrence']['recurrence_algorithm'],
            context.config['Recurrence']['reference_magnitude'],
            context.config['Recurrence']['time_window'])

    t = context.cur_sm.rupture_rate_model.truncated_gutenberg_richter._replace(
        a_value=a_m,
        b_value=bval,
        min_magnitude=context.config['Recurrence']['reference_magnitude'])

    context.cur_sm.rupture_rate_model = \
        context.cur_sm.rupture_rate_model._replace(
                                        truncated_gutenberg_richter=t)

    context.cur_sm.recurrence_sigb = sigb
    context.cur_sm.recurrence_siga_m = siga_m

    LOGGER.debug("Bvalue: %3.3f, Sigma_b: %3.3f, Avalue: %3.3f, Sigma_a: %3.3f"
        % (bval, sigb, a_m, siga_m))
