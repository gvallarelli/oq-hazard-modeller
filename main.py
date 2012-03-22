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
