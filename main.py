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


import logging

from mtoolkit.console import cmd_line, build_logger
from mtoolkit.workflow import Context, PipeLineBuilder, Workflow
from mtoolkit.jobs import (read_eq_catalog, create_catalog_matrix,
                            create_default_values, read_source_model)
from mtoolkit.catalog_filter import SourceModelCatalogFilter

from mtoolkit.nrml import AreaSourceWriter


if __name__ == '__main__':

    CMD_LINE_ARGS = cmd_line()

    if CMD_LINE_ARGS:

        INPUT_CONFIG_FILENAME = CMD_LINE_ARGS.input_file[0]

        LOG_LEVEL = logging.DEBUG if CMD_LINE_ARGS.detailed else logging.INFO

        build_logger(LOG_LEVEL)

        CONTEXT = Context(INPUT_CONFIG_FILENAME)

        PIPELINE_PREPROCESSING = PipeLineBuilder().build(
                CONTEXT.config,
                PipeLineBuilder.PREPROCESSING_JOBS_CONFIG_KEY,
                [read_eq_catalog, read_source_model, create_catalog_matrix,
                create_default_values])

        PIPELINE_PROCESSING = PipeLineBuilder().build(
                CONTEXT.config,
                PipeLineBuilder.PROCESSING_JOBS_CONFIG_KEY)

        SM_CATALOG_FILTER = SourceModelCatalogFilter()

        WORKFLOW = Workflow(PIPELINE_PREPROCESSING, PIPELINE_PROCESSING)

        WORKFLOW.start(CONTEXT, SM_CATALOG_FILTER)

        WRITER = AreaSourceWriter(CONTEXT.config['result_file'])
        WRITER.serialize(CONTEXT.sm_definitions)
