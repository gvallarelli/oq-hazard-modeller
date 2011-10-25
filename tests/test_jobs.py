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


import unittest
import numpy as np

from mtoolkit.eqcatalog import EqEntryReader
from mtoolkit.jobs import load_config_file, read_eq_catalog, apply_declustering
from mtoolkit.declustering import gardner_knopoff_decluster

from tests.test_utils import get_data_path, ROOT_DIR, DATA_DIR


class JobsTestCase(unittest.TestCase):

    def setUp(self):
        self.context = {'config_filename': get_data_path(
            'config.yml', ROOT_DIR),
            'config': {}}
        self.eq_catalog_filename = get_data_path(
            'ISC_small_data.csv', DATA_DIR)

    def test_load_config_file(self):
        expected_config_dict = {
            'apply_processing_steps': None,
            'pprocessing_result_file': 'path_to_file',
            'GardnerKnopoff': {'time_dist_windows': False,
                    'foreshock_time_window': 0},
            'result_file': 'path_to_file',
            'eq_catalog_file': 'path_to_file',
            'preprocessing_steps': ['GardnerKnopoff'],
            'source_model_file': 'path_to_file'}

        load_config_file(self.context)

        self.assertEqual(expected_config_dict, self.context['config'])

    def test_read_eq_catalog(self):
        self.context['config']['eq_catalog_file'] = self.eq_catalog_filename
        expected_first_eq_entry = {'eventID': 1, 'Agency': 'AAA', 'month': 1,
                'depthError': 0.5, 'second': 13.0, 'SemiMajor90': 2.43,
                'year': 2000, 'ErrorStrike': 298.0, 'timeError': 0.02,
                'sigmamb': '', 'latitude': 44.368, 'sigmaMw': 0.355,
                'sigmaMs': '', 'Mw': 1.71, 'Ms': '',
                'Identifier': 20000102034913, 'day': 2, 'minute': 49,
                'hour': 3, 'mb': '', 'SemiMinor90': 1.01, 'longitude': 7.282,
                'depth': 9.3, 'ML': 1.7, 'sigmaML': 0.1}

        read_eq_catalog(self.context)

        self.assertEqual(10, len(self.context['eq_catalog']))
        self.assertEqual(expected_first_eq_entry,
                self.context['eq_catalog'][0])

    def test_apply_declustering(self):
        #Reading eq catalog
        reader = EqEntryReader(self.eq_catalog_filename)
        eq_entries = []
        for eq_entry in reader.read():
            eq_entries.append(eq_entry)

        #Creating numpy matrix
        matrix = []
        attributes = ['year', 'month', 'day', 'longitude', 'latitude', 'Mw']
        for eq_entry in eq_entries:
            matrix.append([eq_entry[attribute] for attribute in attributes])
        numpy_matrix = np.array(matrix)

        #Applying declustering
        vcl, vmain_shock, flag_vector = gardner_knopoff_decluster(numpy_matrix)

        load_config_file(self.context)
        #eq_catalog_file is undefined in the config file
        self.context['config']['eq_catalog_file'] = self.eq_catalog_filename
        read_eq_catalog(self.context)
        apply_declustering(self.context)

        self.assertTrue(np.array_equal(vcl, self.context['vcl']))
        self.assertTrue(np.array_equal(vmain_shock,
                self.context['vmain_shock']))
        self.assertTrue(np.array_equal(flag_vector,
                self.context['flag_vector']))
