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

from mock import Mock

import numpy as np

import filecmp

import unittest

from tests.helper import create_context

from mtoolkit.source_model import (AreaSource, AREA_BOUNDARY, POINT,
                                    TRUNCATED_GUTEN_RICHTER,
                                    RUPTURE_RATE_MODEL,
                                    MAGNITUDE,
                                    RUPTURE_DEPTH_DISTRIB,
                                    default_area_source)

from mtoolkit.jobs import (read_eq_catalog, read_source_model,
                           gardner_knopoff, afteran, stepp,
                           store_preprocessed_catalog,
                           store_completeness_table,
                           retrieve_completeness_table,
                           recurrence,
                           create_default_source_model,
                           maximum_magnitude)

from nrml.nrml_xml import get_data_path, DATA_DIR

RUPTURE_KEY = 'rupture_rate_model'


class JobsTestCase(unittest.TestCase):

    def setUp(self):

        self.context_jobs = create_context('config_jobs.yml')

        self.expected_preprocessed_catalogue = get_data_path(
            'expected_preprocessed_catalogue.csv', DATA_DIR)

        self.expected_preprocessed_ctable = get_data_path(
            'expected_completeness_table.csv', DATA_DIR)

    def test_read_eq_catalog(self):
        expected_first_eq_entry = {'eventID': 1, 'Agency': 'AAA', 'month': 1,
                'depthError': 0.5, 'second': 13.0, 'SemiMajor90': 2.43,
                'year': 2000, 'ErrorStrike': 298.0, 'timeError': 0.02,
                'sigmamb': '', 'latitude': 44.368, 'sigmaMw': 0.355,
                'sigmaMs': '', 'Mw': 1.71, 'Ms': '',
                'Identifier': 20000102034913, 'day': 2, 'minute': 49,
                'hour': 3, 'mb': '', 'SemiMinor90': 1.01, 'longitude': 7.282,
                'depth': 9.3, 'ML': 1.7, 'sigmaML': 0.1}
        read_eq_catalog(self.context_jobs)

        self.assertEqual(10, len(self.context_jobs.eq_catalog))

        self.assertEqual(expected_first_eq_entry,
                self.context_jobs.eq_catalog[0])

    def test_read_smodel(self):
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
        read_source_model(self.context_jobs)

        self.assertEqual(1, len(self.context_jobs.sm_definitions))

        self.assertEqual(asource,
                self.context_jobs.sm_definitions[0])

    def test_create_default_source_model(self):
        default_as = [default_area_source()]
        create_default_source_model(self.context_jobs)

        self.assertEqual(default_as, self.context_jobs.sm_definitions)

    def test_parameters_gardner_knopoff(self):
        mocked_func = Mock(return_value=([], [], []))
        self.context_jobs.map_sc['gardner_knopoff'] = mocked_func
        gardner_knopoff(self.context_jobs)

        self.assertTrue(mocked_func.called)

        mocked_func.assert_called_with(None, 'GardnerKnopoff', 0.5)

    def test_parameters_afteran(self):
        mocked_func = Mock(return_value=([], [], []))
        self.context_jobs.map_sc['afteran'] = mocked_func
        afteran(self.context_jobs)

        self.assertTrue(mocked_func.called)

        mocked_func.assert_called_with(None, 'Uhrhammer', 150.8)

    def test_parameters_stepp(self):
        self.context_jobs.working_catalog = np.array([[1, 2, 3, 4, 5, 6]])
        mocked_func = Mock()
        self.context_jobs.map_sc['stepp'] = mocked_func
        stepp(self.context_jobs)

        self.assertTrue(mocked_func.called)

        mocked_func.assert_called_with(
            self.context_jobs.working_catalog[:, 0],
            self.context_jobs.working_catalog[:, 5], 0.1, 5, 0.2, True)

    def test_param_recurrence(self):
        self.context_jobs.current_filtered_eq = np.array([[1, 2, 3, 4, 5, 6]])
        self.context_jobs.completeness_table = np.array([[1, 0]])
        self.context_jobs.cur_sm = Mock()
        mocked_func = Mock(return_value=(0, 0, 0, 0))
        self.context_jobs.map_sc['recurrence'] = mocked_func
        recurrence(self.context_jobs)

        self.assertTrue(mocked_func.called)

        mocked_func.assert_called_with(
            self.context_jobs.current_filtered_eq[:, 0],
            self.context_jobs.current_filtered_eq[:, 5],
            self.context_jobs.completeness_table,
            0.5, 'Weichert', 1.1, 0.3)

    def test_store_catalog_in_csv_after_preprocessing(self):
        self.context_jobs.selected_eq_vector = np.array(
            [0, 0, 0, 1, 1, 0, 1, 0, 1, 0])
        read_eq_catalog(self.context_jobs)
        self.context_jobs.catalog_matrix = self.context_jobs.eq_catalog
        store_preprocessed_catalog(self.context_jobs)

        self.assertTrue(filecmp.cmp(self.expected_preprocessed_catalogue,
                self.context_jobs.config['pprocessing_result_file']))

    def test_store_completeness_table(self):
        self.context_jobs.completeness_table = np.array([
            [1991., 4.], [1991., 4.2], [1961., 4.4],
            [1961., 4.6], [1961., 4.8], [1961., 5.],
            [1961., 5.2], [1912., 5.4], [1912., 5.6],
            [1911., 5.8], [1911., 6.], [1911., 6.2],
            [1911., 6.4], [1911., 6.6], [1911., 6.8],
            [1911., 7.], [1911., 7.2]])
        store_completeness_table(self.context_jobs)

        self.assertTrue(filecmp.cmp(
            self.expected_preprocessed_ctable,
            self.context_jobs.config['completeness_table_file']))

    def test_retrieve_completeness_table(self):
        expected_table = np.array([
            [1991., 4.], [1991., 4.2], [1961., 4.4],
            [1961., 4.6], [1961., 4.8], [1961., 5.],
            [1961., 5.2], [1912., 5.4], [1912., 5.6],
            [1911., 5.8], [1911., 6.], [1911., 6.2],
            [1911., 6.4], [1911., 6.6], [1911., 6.8],
            [1911., 7.], [1911., 7.2]])
        retrieve_completeness_table(self.context_jobs)

        self.assertTrue(np.array_equal(expected_table,
            self.context_jobs.completeness_table))

    def test_param_maximum_magnitude(self):
        self.context_jobs.current_filtered_eq = np.array(
            [[1, 2, 3, 4, 5, 6, 7]])
        cur_sm = Mock()
        cur_sm.rupture_rate_model.truncated_gutenberg_richter.b_value = 4.2
        cur_sm.recurrence_sigb = 0.3
        self.context_jobs.cur_sm = cur_sm
        mocked_func = Mock(return_value=(0, 0))
        self.context_jobs.map_sc['maximum_magnitude'] = mocked_func
        maximum_magnitude(self.context_jobs)

        self.assertTrue(mocked_func.called)

        mocked_func.assert_called_with(
            np.array([1]), np.array([6]), np.array([7]), 4.2, 0.3,
            'Cumulative_Moment', 1.0E-5, 1000, 5.8, 0.3, 200, 51, 100)
