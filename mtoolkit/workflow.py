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
to process a series of jobs in a sequential
order. The order is determined by the queue of jobs.
"""

import yaml

from mtoolkit.jobs import (gardner_knopoff, stepp, recurrence,
                            read_eq_catalog, read_source_model,
                            create_default_source_model,
                            create_catalog_matrix,
                            create_default_values)

from mtoolkit.scientific.declustering import gardner_knopoff_decluster
from mtoolkit.scientific.completeness import stepp_analysis
from mtoolkit.scientific.recurrence import recurrence_analysis


class PipeLine(object):
    """
    PipeLine allows to create a queue of
    jobs and execute them in order.
    """

    def __init__(self, name, jobs_list=None):
        """
        Initialize a PipeLine object having
        attributes: name and jobs, a list
        of callable objects.
        """

        self.name = name
        self.jobs = []
        if jobs_list != None:
            self.jobs = jobs_list

    def __eq__(self, other):
        """Equal operator for pipeline"""

        return self.name == other.name \
                and self.jobs == other.jobs

    def __ne__(self, other):
        """Not equal operator for pipeline"""

        return not self.__eq__(other)

    def add_job(self, a_job):
        """Append a new job the to queue"""

        self.jobs.append(a_job)

    def run(self, context):
        """
        Run all the jobs in queue,
        where each job take input data
        and write the results
        of calculation in context.
        If logging is triggered by cmdline
        each job is decorated by adding
        logging statements.
        """

        for job in self.jobs:
            job(context)


class PipeLineBuilder(object):
    """
    PipeLineBuilder allows to build a PipeLine
    by assembling all the required jobs
    specified in the config file.
    """

    PREPROCESSING_JOBS_CONFIG_KEY = 'preprocessing_jobs'
    PROCESSING_JOBS_CONFIG_KEY = 'processing_jobs'

    def __init__(self):
        self.map_job_callable = {'GardnerKnopoff': gardner_knopoff,
                                  'Stepp': stepp,
                                  'Recurrence': recurrence}

    def build(self, config, pipeline_type):
        """
        Build method creates the pipeline by
        assembling all the steps required.
        The steps described in the config
        could be preprocessing or processing
        steps.
        """

        if pipeline_type == self.PREPROCESSING_JOBS_CONFIG_KEY:

            if config['source_model_file']:
                source_model_creation = read_source_model
            else:
                source_model_creation = create_default_source_model

            pipeline = PipeLine(pipeline_type,
                    [read_eq_catalog, source_model_creation,
                    create_catalog_matrix, create_default_values])
        else:
            pipeline = PipeLine(pipeline_type)

        if config[pipeline_type] != None:
            for job in config[pipeline_type]:
                if job in self.map_job_callable:
                    pipeline.add_job(self.map_job_callable[job])
                else:
                    raise RuntimeError('Invalid job: %s' % job)

        return pipeline


class Context(object):
    """
    Context allows to read the config file
    and store preprocessing/processing steps
    intermediate results.
    """

    def __init__(self, config_filename=None):
        self.config = dict()
        self.map_sc = {'gardner_knopoff': gardner_knopoff_decluster,
                        'stepp': stepp_analysis,
                        'recurrence': recurrence_analysis}

        if config_filename:
            config_file = open(config_filename, 'r')
            self.config = yaml.load(config_file)
        self.catalog_matrix = None


class Workflow(object):
    """
    Workflow is the object responsible
    for dealing with preprocessing and
    processing pipelines
    """

    def __init__(self, preprocessing_pipeline, processing_pipeline):
        self.preprocessing_pipeline = preprocessing_pipeline
        self.processing_pipeline = processing_pipeline

    def start(self, context, catalog_filter):
        """
        Execute the main workflow
        """
        self.preprocessing_pipeline.run(context)
        if context.config['apply_processing_jobs']:
            for sm, filtered_eq in catalog_filter.filter_eqs(
                    context.sm_definitions, context.catalog_matrix):

                context.cur_sm = sm
                context.current_filtered_eq = filtered_eq
                self.processing_pipeline.run(context)
