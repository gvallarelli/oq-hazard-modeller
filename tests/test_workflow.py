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

from mtoolkit.workflow import PipeLine, PipeLineBuilder, Context
from mtoolkit.workflow import PipeLineManager
from mtoolkit.jobs import read_eq_catalog, create_catalog_matrix
from mtoolkit.jobs import gardner_knopoff, stepp, recurrence
from mtoolkit.utils import get_data_path, DATA_DIR


class ContextTestCase(unittest.TestCase):

    def setUp(self):
        self.context_preprocessing = Context(
            get_data_path('config_preprocessing.yml', DATA_DIR))

    def test_load_config_file(self):
        expected_config_dict = {
            'apply_processing_jobs': None,
            'pprocessing_result_file': 'path_to_file',
            'GardnerKnopoff': {'time_dist_windows': False,
                    'foreshock_time_window': 0},
            'Stepp': {'increment_lock': True,
            'magnitude_windows': 0.2,
            'sensitivity': 0.1,
            'time_window': 5},
            'result_file': 'path_to_file',
            'eq_catalog_file': 'tests/data/ISC_correct.csv',
            'preprocessing_jobs': ['GardnerKnopoff', 'Stepp'],
            'source_model_file': 'path_to_file'}

        self.assertEqual(expected_config_dict,
            self.context_preprocessing.config)


class PipeLineTestCase(unittest.TestCase):

    def setUp(self):

        def square_job(context):
            value = context.number
            context.number = value * value

        def double_job(context):
            value = context.number
            context.number = 2 * value

        self.square_job = square_job
        self.double_job = double_job

        self.pipeline_name = 'square pipeline'
        self.pipeline = PipeLine(self.pipeline_name)

        self.context_preprocessing = Context(
            get_data_path('config_preprocessing.yml', DATA_DIR))
        self.context_preprocessing.number = 2

    def test_run_jobs(self):
        self.pipeline.add_job(self.square_job)
        self.pipeline.add_job(self.double_job)
        self.pipeline.run(self.context_preprocessing)

        self.assertEqual(8, self.context_preprocessing.number)

        # Change jobs order
        self.pipeline.jobs.reverse()
        # Reset context to a base value
        self.context_preprocessing.number = 2
        self.pipeline.run(self.context_preprocessing)

        self.assertEqual(16, self.context_preprocessing.number)


class PipeLineBuilderTestCase(unittest.TestCase):

    def setUp(self):
        self.pipeline_builder = PipeLineBuilder()
        self.context_preprocessing = Context(
            get_data_path('config_preprocessing.yml', DATA_DIR))
        self.context_processing = Context(
            get_data_path('config_processing.yml', DATA_DIR))

    def test_build_pipeline(self):
        # Two different kinds of pipeline can be built:
        # preprocessing and processing pipeline

        expected_preprocessing_pipeline = PipeLine('preprocessing_jobs')
        expected_preprocessing_pipeline.add_job(read_eq_catalog)
        expected_preprocessing_pipeline.add_job(create_catalog_matrix)
        expected_preprocessing_pipeline.add_job(gardner_knopoff)
        expected_preprocessing_pipeline.add_job(stepp)

        expected_processing_pipeline = PipeLine('processing_jobs')
        expected_processing_pipeline.add_job(recurrence)

        pprocessing_built_pipeline = self.pipeline_builder.build(
            self.context_preprocessing.config,
            PipeLineBuilder.PREPROCESSING_JOBS_CONFIG_KEY,
            [read_eq_catalog, create_catalog_matrix])

        processing_built_pipeline = self.pipeline_builder.build(
            self.context_processing.config,
            PipeLineBuilder.PROCESSING_JOBS_CONFIG_KEY)

        self.assertEqual(expected_preprocessing_pipeline,
            pprocessing_built_pipeline)
        self.assertEqual(expected_processing_pipeline,
            processing_built_pipeline)

    def test_non_existent_job_raise_exception(self):
        invalid_job = 'comb a quail\'s hair'
        self.context_preprocessing.config['preprocessing_jobs'] = [invalid_job]
        self.context_processing.config['processing_jobs'] = [invalid_job]

        self.assertRaises(RuntimeError, self.pipeline_builder.build,
                self.context_preprocessing.config,
                PipeLineBuilder.PREPROCESSING_JOBS_CONFIG_KEY)

        self.assertRaises(RuntimeError, self.pipeline_builder.build,
                self.context_processing.config,
                PipeLineBuilder.PROCESSING_JOBS_CONFIG_KEY)

    def test_manager_execute_preprocessing_pipeline(self):
        context = Context()
        context.sm_definitions = []
        context.config["apply_processing_jobs"] = True

        def run(context):
            context.run = True

        preprocessing = PipeLine("preprocessing")
        preprocessing.add_job(run)

        manager = PipeLineManager(context, preprocessing, None)
        manager.start()

        self.assertTrue(context.run)

    def test_manager_execute_processing_pipeline(self):
        context = Context()

        context.config['apply_processing_jobs'] = True

        eq_internal_point = [2000, 1, 2, -0.25, 0.25]
        eq_side_point = [2000, 1, 2, -0.5, 0.25]
        eq_external_point = [2000, 1, 2, 0.5, 0.25]
        eq_events = np.array([eq_internal_point,
                eq_side_point, eq_external_point])
        context.catalog_matrix = eq_events
        sm = {'area_boundary':
            [-0.5, 0.0, -0.5, 0.5, 0.0, 0.5, 0.0, 0.0]}
        context.sm_definitions = [sm]

        def run(context):
            self.assertEqual(sm, context.current_sm)
            self.assertTrue(np.array_equal(np.array([eq_internal_point]),
                context.current_filtered_eq))

        pipeline_preprocessing = PipeLine(None)
        pipeline_processing = PipeLine(None)
        pipeline_processing.add_job(run)

        pipeline_manager = PipeLineManager(context,
            pipeline_preprocessing, pipeline_processing)

        pipeline_manager.start()
