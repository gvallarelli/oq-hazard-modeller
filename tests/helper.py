# -*- coding: utf-8 -*-

# Copyright (c) 2010-2012, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.


"""
This module provide helper functions used in
tests.
"""

from mtoolkit.workflow import (Context, PreprocessingBuilder,
                                ProcessingBuilder, Workflow)

from mtoolkit.catalog_filter import CatalogFilter, SourceModelCatalogFilter

from nrml.nrml_xml import get_data_path, DATA_DIR


def create_workflow(config):
    """Create a workflow based on the config"""

    preprocessing_pipeline = PreprocessingBuilder().build(config)

    processing_pipeline = ProcessingBuilder().build(config)

    return Workflow(preprocessing_pipeline, processing_pipeline)


def create_context(filename=None):
    """Create a context using config file"""

    return Context(get_data_path(filename, DATA_DIR))


def run(workflow, context):
    """Run the workflow with source model filtering"""

    return workflow.start(context, CatalogFilter(SourceModelCatalogFilter()))
