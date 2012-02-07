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