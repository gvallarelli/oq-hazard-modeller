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
The purpose of this module is to provide test methods
that compare equivalent workflows
"""

import unittest

from mtoolkit.workflow import Context

from tests.helper import create_workflow, run


class EquivalentWorkflowsTestCase(unittest.TestCase):

    # Todo: Add 'MLE'
    recurrence_alg = ['Weichert']

    def evaluate_values(self, preprocessed_sm, no_preprocessed_sm):
        for i in range(len(preprocessed_sm)):
            self.assertEqual(preprocessed_sm[i].rupture_rate_model,
                no_preprocessed_sm[i].rupture_rate_model)

            self.assertEqual(preprocessed_sm[i].recurrence_sigb,
                no_preprocessed_sm[i].recurrence_sigb)

            self.assertEqual(preprocessed_sm[i].recurrence_siga_m,
                no_preprocessed_sm[i].recurrence_siga_m)

    def run_config(self, wprep, wnoprep):
        for alg in EquivalentWorkflowsTestCase.recurrence_alg:
            self.config_prep['Recurrence']['recurrence_algorithm'] = alg
            self.config_noprep['Recurrence']['recurrence_algorithm'] = alg
            self.context_prep.config = self.config_prep
            self.context_noprep.config = self.config_noprep
            run(wprep, self.context_prep)
            run(wnoprep, self.context_noprep)

            self.evaluate_values(self.context_prep.sm_definitions,
                self.context_noprep.sm_definitions)

    def setUp(self):
        self.context_prep = Context()
        self.context_noprep = Context()

        self.config_prep = {
            'eq_catalog_file': 'tests/data/completeness_input_test.csv',
            'source_model_file': 'tests/data/area_source_model_processing.xml',
            'result_file': 'tests/data/output.xml',
            'apply_processing_jobs': True,
            'pprocessing_result_file': 'tests/data/preprocessed_catalogue.csv',
            'completeness_table_file': 'tests/data/completeness_table.csv',
            'preprocessing_jobs': None,

            'Afteran': {
                'time_dist_windows': 'Uhrhammer',
                'time_window': 60.0
            },
            'GardnerKnopoff': {
                'time_dist_windows': None,
                'foreshock_time_window': 0.5
            },

            'Stepp': {'increment_lock': True,
                'magnitude_windows': 0.2,
                'sensitivity': 0.1,
                'time_window': 1
            },

            'processing_jobs': ['Recurrence'],
            'Recurrence': {'magnitude_window': 0.2,
                'recurrence_algorithm': None,
                'reference_magnitude': 3.7,
                'time_window': 1.0
            }
        }

        self.config_noprep = {
            'eq_catalog_file': 'tests/data/preprocessed_catalogue.csv',
            'source_model_file': 'tests/data/area_source_model_processing.xml',
            'result_file': 'tests/data/output.xml',
            'apply_processing_jobs': True,
            'completeness_table_file': 'tests/data/completeness_table.csv',
            'preprocessing_jobs': None,
            'processing_jobs': ['Recurrence'],
            'Recurrence': {'magnitude_window': 0.2,
                'recurrence_algorithm': None,
                'reference_magnitude': 3.7,
                'time_window': 1.0
            }
        }

    # GardnerKnopoff, Recurrence
    def test_first_configuration(self):
        self.config_prep['preprocessing_jobs'] = ['GardnerKnopoff']
        wprep = create_workflow(self.config_prep)
        wnoprep = create_workflow(self.config_noprep)
        self.run_config(wprep, wnoprep)

    # Afteran, Recurrence
    def test_second_configuration(self):
        self.config_prep['preprocessing_jobs'] = ['Afteran']
        wprep = create_workflow(self.config_prep)
        wnoprep = create_workflow(self.config_noprep)
        self.run_config(wprep, wnoprep)

    # GardnerKnopoff, Stepp, Recurrence
    def test_third_configuration(self):
        self.config_prep['preprocessing_jobs'] = ['GardnerKnopoff', 'Stepp']
        wprep = create_workflow(self.config_prep)
        wnoprep = create_workflow(self.config_noprep)
        self.run_config(wprep, wnoprep)

    # Afteran, Stepp, Recurrence
    def test_fourth_configuration(self):
        self.config_prep['preprocessing_jobs'] = ['Afteran', 'Stepp']
        wprep = create_workflow(self.config_prep)
        wnoprep = create_workflow(self.config_noprep)
        self.run_config(wprep, wnoprep)

    # Stepp, Recurrence
    def test_fifth_configuration(self):
        self.config_prep['preprocessing_jobs'] = ['Stepp']
        wprep = create_workflow(self.config_prep)
        wnoprep = create_workflow(self.config_noprep)
        self.run_config(wprep, wnoprep)
