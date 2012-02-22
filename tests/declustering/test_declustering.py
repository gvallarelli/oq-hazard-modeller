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


import unittest
import numpy as np

from mtoolkit.scientific.declustering import (TDW_GARDNERKNOPOFF,
    TDW_GRUENTHAL, TDW_UHRHAMMER, gardner_knopoff_decluster, afteran_decluster)

from tests.declustering.data._declustering_test_data import (
    CATALOG_MATRIX_ALL_CLUSTER, CATALOG_MATRIX_NO_CLUSTERS)


class DeclusteringTestCase(unittest.TestCase):

    def setUp(self):
        self.catalog_matrix_all_cluster = np.array(CATALOG_MATRIX_ALL_CLUSTER)

        self.catalog_matrix_no_clusters = np.array(CATALOG_MATRIX_NO_CLUSTERS)

        self.time_dist_windows_options = [TDW_GARDNERKNOPOFF,
                TDW_GRUENTHAL, TDW_UHRHAMMER]

        self.foreshock_time_windows = [0.0, 0.1, 0.2]

        self.time_window_in_days = [10, 30, 60]

    def evaluate_results_gardner(self, catalog_matrix, exp_vcl,
            exp_vmain_shock, exp_flag_vector):

        for tdw in self.time_dist_windows_options:
            for ftw in self.foreshock_time_windows:

                vcl, vmain_shock, flag_vector = gardner_knopoff_decluster(
                    catalog_matrix, tdw, ftw)

                self.assertTrue(np.array_equal(exp_vcl, vcl))

                self.assertTrue(np.array_equal(
                        exp_vmain_shock, vmain_shock))

                self.assertTrue(np.array_equal(
                        exp_flag_vector, flag_vector))

    def evaluate_results_afteran(self, catalog_matrix, exp_vcl,
        exp_vmain_shock, exp_flag_vector):

        for tdw in self.time_dist_windows_options:
            for tw in self.time_window_in_days:

                vcl, vmain_shock, flag_vector = afteran_decluster(
                    catalog_matrix, tdw, tw)

                self.assertTrue(np.array_equal(exp_vcl, vcl))

                self.assertTrue(np.array_equal(
                        exp_vmain_shock, vmain_shock))

                self.assertTrue(np.array_equal(
                        exp_flag_vector, flag_vector))

    def test_gardner_knopoff_all_events_within_a_cluster(self):

        expected_vcl = np.array([1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        expected_vmain_shock = np.array([[1.9820e+03, 5.0000e+00, 3.000e+00,
                2.0596e+01, 3.8545e+01, 7.2000e+00, 1.0000e-01]])

        expected_flag_vector = np.array([0, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        self.evaluate_results_gardner(self.catalog_matrix_all_cluster,
                expected_vcl, expected_vmain_shock, expected_flag_vector)

    def test_gardner_knopoff_no_events_within_a_cluster(self):

        expected_vcl = expected_flag_vector = np.array([0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        expected_vmain_shock = self.catalog_matrix_no_clusters

        self.evaluate_results_gardner(self.catalog_matrix_no_clusters,
                expected_vcl, expected_vmain_shock, expected_flag_vector)

    def test_afteran_all_events_within_a_cluster(self):

        expected_vcl = np.array([1, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        expected_vmain_shock = np.array([[1.9820e+03, 5.0000e+00, 3.000e+00,
                2.0596e+01, 3.8545e+01, 7.2000e+00, 1.0000e-01]])

        expected_flag_vector = np.array([0, 1, 1, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

        self.evaluate_results_afteran(self.catalog_matrix_all_cluster,
            expected_vcl, expected_vmain_shock, expected_flag_vector)

    def test_afteran_no_events_within_a_cluster(self):

        expected_vcl = expected_flag_vector = np.array([0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        expected_vmain_shock = self.catalog_matrix_no_clusters

        self.evaluate_results_afteran(self.catalog_matrix_no_clusters,
                expected_vcl, expected_vmain_shock, expected_flag_vector)
