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

from tests.helper import create_context, create_workflow, run

from mtoolkit.jobs import gardner_knopoff, afteran


class DeclusteringTestCase(unittest.TestCase):

    def test_gardner_knopoff(self):
        context = create_context('config_gardner_knopoff.yml')

        workflow = create_workflow(context.config)
        run(workflow, context)

        expected_vmain_shock = np.delete(
            context.catalog_matrix, [4, 10, 19], 0)

        expected_vcl = np.array([0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0,
            0, 0, 0, 0, 6])

        expected_flag_vector = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 0, 1])

        gardner_knopoff(context)

        self.assertTrue(np.array_equal(expected_vmain_shock,
                context.working_catalog))
        self.assertTrue(np.array_equal(expected_vcl, context.vcl))
        self.assertTrue(np.array_equal(expected_flag_vector,
                context.flag_vector))

    def test_afteran(self):
        context = create_context('config_afteran.yml')

        workflow = create_workflow(context.config)
        run(workflow, context)

        expected_vmain_shock = np.delete(
            context.catalog_matrix, [4, 10, 19], 0)

        expected_vcl = np.array([0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 3, 3])

        expected_flag_vector = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
            0, 0, 0, 0, 0, 0, 1])

        afteran(context)

        self.assertTrue(np.array_equal(expected_vmain_shock,
                context.working_catalog))

        self.assertTrue(np.array_equal(expected_vcl, context.vcl))

        self.assertTrue(np.array_equal(expected_flag_vector,
                context.flag_vector))
