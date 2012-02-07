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

import numpy as np
import filecmp
import unittest


from tests.helper import create_workflow, create_context, run

from mtoolkit.source_model import (AreaSource, AREA_BOUNDARY, POINT,
                                    TRUNCATED_GUTEN_RICHTER,
                                    RUPTURE_RATE_MODEL,
                                    MAGNITUDE,
                                    RUPTURE_DEPTH_DISTRIB,
                                    default_area_source)

from mtoolkit.jobs import (read_eq_catalog, read_source_model,
                           gardner_knopoff, afteran,
                           recurrence,
                           create_default_source_model)

from nrml.nrml_xml import get_data_path, DATA_DIR

RUPTURE_KEY = 'rupture_rate_model'


class JobsTestCase(unittest.TestCase):

    def setUp(self):
        self.context = create_context('config_processing.yml')

        self.eq_catalog_filename = get_data_path(
            'ISC_small_data.csv', DATA_DIR)

        self.smodel_filename = get_data_path(
            'area_source_model.xml', DATA_DIR)

        self.preprocessing_config = get_data_path(
            'config_preprocessing.yml', DATA_DIR)

        self.expected_preprocessed_catalogue = get_data_path(
            'expected_preprocessed_catalogue.csv', DATA_DIR)

        self.expected_preprocessed_ctable = get_data_path(
            'expected_completeness_table.csv', DATA_DIR)

    def test_read_eq_catalog(self):
        self.context.config['eq_catalog_file'] = self.eq_catalog_filename
        expected_first_eq_entry = {'eventID': 1, 'Agency': 'AAA', 'month': 1,
                'depthError': 0.5, 'second': 13.0, 'SemiMajor90': 2.43,
                'year': 2000, 'ErrorStrike': 298.0, 'timeError': 0.02,
                'sigmamb': '', 'latitude': 44.368, 'sigmaMw': 0.355,
                'sigmaMs': '', 'Mw': 1.71, 'Ms': '',
                'Identifier': 20000102034913, 'day': 2, 'minute': 49,
                'hour': 3, 'mb': '', 'SemiMinor90': 1.01, 'longitude': 7.282,
                'depth': 9.3, 'ML': 1.7, 'sigmaML': 0.1}

        read_eq_catalog(self.context)

        self.assertEqual(10, len(self.context.eq_catalog))
        self.assertEqual(expected_first_eq_entry,
                self.context.eq_catalog[0])

    def test_read_smodel(self):
        self.context.config['source_model_file'] = self.smodel_filename

        asource = AreaSource()
        asource.nrml_id = "n1"
        asource.source_model_id = "sm1"
        asource.area_source_id = "src03"
        asource.name = "Quito"
        asource.tectonic_region = "Active Shallow Crust"

        area_boundary = [-122.5, 37.5, -121.5,
                            37.5, -121.5, 38.5,
                            -122.5, 38.5]
        asource.area_boundary = AREA_BOUNDARY("urn:ogc:def:crs:EPSG::4326",
                [POINT(area_boundary[i],
                    area_boundary[i + 1])
                    for i in xrange(0, len(area_boundary), 2)])

        truncated_gutenberg_richter = TRUNCATED_GUTEN_RICHTER(
            5.0, 0.8, 5.0, 7.0, "ML")

        strike = 0.0
        dip = 90.0
        rake = 0.0

        asource.rupture_rate_model = RUPTURE_RATE_MODEL(
            truncated_gutenberg_richter, strike, dip, rake)

        magnitude = MAGNITUDE("ML", [6.0, 6.5, 7.0])
        depth = [5000.0, 3000.0, 0.0]

        asource.rupture_depth_dist = RUPTURE_DEPTH_DISTRIB(magnitude, depth)

        asource.hypocentral_depth = 5000.0

        read_source_model(self.context)
        self.assertEqual(1, len(self.context.sm_definitions))
        self.assertEqual(asource,
                self.context.sm_definitions[0])

    def test_create_default_source_model(self):
        default_as = [default_area_source()]

        create_default_source_model(self.context)

        self.assertEqual(default_as, self.context.sm_definitions)

    def test_parameters_gardner_knopoff(self):
        context = create_context('config_gardner_knopoff.yml')
        context.working_catalog = None

        context.catalog_matrix = []

        def assert_parameters(data, time_dist_windows, foreshock_time_window):
            self.assertEquals("GardnerKnopoff", time_dist_windows)
            self.assertEquals(0.5, foreshock_time_window)
            return [], [], []

        context.map_sc['gardner_knopoff'] = assert_parameters
        gardner_knopoff(context)

    def test_parameters_afteran(self):
        context = create_context('config_afteran.yml')

        context.catalog_matrix = []

        def assert_parameters(data, time_dist_windows, time_window):
            self.assertEquals("Uhrhammer", time_dist_windows)
            self.assertEquals(150.8, time_window)
            return [], [], []

        context.map_sc['afteran'] = assert_parameters
        afteran(context)

    def test_parameters_stepp(self):
        context = create_context('config_stepp.yml')

        workflow = create_workflow(context.config)

        def assert_parameters(year, mw, magnitude_windows, time_window,
                sensitivity, iloc):
            self.assertEqual(time_window, 5)
            self.assertEqual(magnitude_windows, 0.1)
            self.assertEqual(sensitivity, 0.2)
            self.assertTrue(iloc)
            return np.array([[0, 0]])

        context.map_sc['stepp'] = assert_parameters

        run(workflow, context)

    def test_parameters_recurrence(self):
        self.context.config['Recurrence']['magnitude_window'] = 0.5
        self.context.config['Recurrence']['recurrence_algorithm'] = 'Wiechart'
        self.context.config['Recurrence']['referece_magnitude'] = 1.1
        self.context.config['Recurrence']['time_window'] = 0.3

        # Fake values for used attributes
        self.context.cur_sm = AreaSource()
        tgr = TRUNCATED_GUTEN_RICHTER('', '', '', '', '')
        rrm = RUPTURE_RATE_MODEL(tgr, '', '', '')
        self.context.cur_sm.rupture_rate_model = rrm

        self.context.completeness_table = []
        self.context.current_filtered_eq = np.array([[1, 2, 3, 4, 5, 6]])

        def assert_parameters(year_col, magnitude_col, completeness_table,
            magnitude_window, recurrence_algorithm, reference_magnitude,
            time_window):

            self.assertEqual(magnitude_window, 0.5)
            self.assertEqual(recurrence_algorithm, 'Wiechart')
            self.assertEqual(reference_magnitude, 1.1)
            self.assertEqual(time_window, 0.3)
            return 0.0, 0.0, 0.0, 0.0

        self.context.map_sc['recurrence'] = assert_parameters
        recurrence(self.context)

    def test_store_catalog_in_csv_after_preprocessing(self):
        context = create_context(self.preprocessing_config)
        workflow = create_workflow(context.config)
        run(workflow, context)

        self.assertTrue(filecmp.cmp(self.expected_preprocessed_catalogue,
                context.config['pprocessing_result_file']))

    def test_store_completeness_table(self):
        context = create_context(self.preprocessing_config)
        workflow = create_workflow(context.config)
        run(workflow, context)

        self.assertTrue(filecmp.cmp(
            self.expected_preprocessed_ctable,
            context.config['completeness_table_file']))

    def test_retrieve_completeness_table(self):
        context = create_context(self.preprocessing_config)
        ctable_filename = 'tests/data/expected_completeness_table.csv'
        context.config['preprocessing_jobs'] = None
        context.config['completeness_table_file'] = ctable_filename
        workflow = create_workflow(context.config)
        run(workflow, context)

        expected_table = np.array([[1991.00000, 4.00000],
                                    [1991.00000, 4.20000],
                                    [1961.00000, 4.40000],
                                    [1961.00000, 4.60000],
                                    [1961.00000, 4.80000],
                                    [1961.00000, 5.00000],
                                    [1961.00000, 5.20000],
                                    [1912.00000, 5.40000],
                                    [1912.00000, 5.60000],
                                    [1911.00000, 5.80000],
                                    [1911.00000, 6.00000],
                                    [1911.00000, 6.20000],
                                    [1911.00000, 6.40000],
                                    [1911.00000, 6.60000],
                                    [1911.00000, 6.80000],
                                    [1911.00000, 7.00000],
                                    [1911.00000, 7.20000]])

        self.assertTrue(np.array_equal(expected_table,
            context.completeness_table))
