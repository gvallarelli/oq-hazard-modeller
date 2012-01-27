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

from mtoolkit.workflow import (Context, PreprocessingBuilder,
                                ProcessingBuilder, Workflow)

from nrml.writer import AreaSourceWriter

from mtoolkit.catalog_filter import CatalogFilter, SourceModelCatalogFilter


if __name__ == '__main__':

    CMD_LINE_ARGS = cmd_line()

    if CMD_LINE_ARGS:

        INPUT_CONFIG_FILENAME = CMD_LINE_ARGS.input_file[0]

        LOG_LEVEL = logging.DEBUG if CMD_LINE_ARGS.detailed else logging.INFO

        build_logger(LOG_LEVEL)

        CONTEXT = Context(INPUT_CONFIG_FILENAME)

        PIPELINE_PREPROCESSING = PreprocessingBuilder().build(CONTEXT.config)

        PIPELINE_PROCESSING = ProcessingBuilder().build(CONTEXT.config)

        if CONTEXT.config['source_model_file']:
            CATALOG_FILTER = CatalogFilter(SourceModelCatalogFilter())
        else:
            CATALOG_FILTER = CatalogFilter()

        WORKFLOW = Workflow(PIPELINE_PREPROCESSING, PIPELINE_PROCESSING)
        WORKFLOW.start(CONTEXT, CATALOG_FILTER)

        WRITER = AreaSourceWriter(CONTEXT.config['result_file'])
        WRITER.serialize(CONTEXT.sm_definitions)
