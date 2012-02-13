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


class DeclusteringTestCase(unittest.TestCase):

    def setUp(self):
        self.expected_vmain_shock = np.array([
            [1.961e+03, 1.0e+00, 2.1e+01, 2.059e+01, 3.855e+01, 6.2e+00, 0.1],
            [1.964e+03, 5.0e+00, 2.5e+01, 2.259e+01, 3.952e+01, 5.7e+00, 0.1],
            [1.967e+03, 4.0e+00, 3.0e+01, 2.418e+01, 3.791e+01, 5.2e+00, 0.1],
            [1.970e+03, 7.0e+00, 1.4e+01, 2.225e+01, 3.686e+01, 6.5e+00, 0.1],
            [1.973e+03, 8.0e+00, 5.0e+00, 2.086e+01, 3.387e+01, 6.1e+00, 0.1],
            [1.976e+03, 1.2e+01, 8.0e+00, 2.315e+01, 3.168e+01, 7.2e+00, 0.1],
            [1.979e+03, 1.1e+01, 1.2e+01, 2.586e+01, 3.075e+01, 5.7e+00, 0.1],
            [1.982e+03, 3.0e+00, 4.0e+00, 2.785e+01, 3.089e+01, 6.4e+00, 0.1],
            [1.985e+03, 4.0e+00, 1.4e+01, 2.983e+01, 3.279e+01, 6.8e+00, 0.1],
            [1.988e+03, 1.2e+01, 1.8e+01, 2.344e+01, 3.452e+01, 4.5e+00, 0.1],
            [1.991e+03, 6.0e+00, 2.3e+01, 2.566e+01, 3.358e+01, 5.0e+00, 0.1],
            [1.994e+03, 8.0e+00, 2.7e+01, 2.847e+01, 3.496e+01, 4.9e+00, 0.1],
            [1.997e+03, 6.0e+00, 3.0e+01, 2.589e+01, 3.610e+01, 5.9e+00, 0.1],
            [2.000e+03, 3.0e+00, 1.0e+00, 2.017e+01, 3.013e+01, 6.4e+00, 0.1],
            [2.003e+03, 2.0e+00, 9.0e+00, 2.729e+01, 3.800e+01, 6.0e+00, 0.1],
            [2.006e+03, 1.0e+00, 1.0e+01, 2.570e+01, 3.987e+01, 5.4e+00, 0.1],
            [2.009e+03, 1.0e+01, 1.3e+01, 2.990e+01, 3.686e+01, 6.3e+00, 0.1]])

        self.expected_flag_vector = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 0, 0, 0, 1])

    def test_gardner_knopoff(self):
        context = create_context('config_gardner_knopoff.yml')
        workflow = create_workflow(context.config)
        run(workflow, context)

        expected_vcl = np.array([0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0,
            0, 0, 0, 0, 6])
        print context.working_catalog[:, 6]
        self.assertTrue(np.array_equal(self.expected_vmain_shock,
                context.working_catalog))
        self.assertTrue(np.array_equal(expected_vcl, context.vcl))
        self.assertTrue(np.array_equal(self.expected_flag_vector,
                context.flag_vector))

    def test_afteran(self):
        context = create_context('config_afteran.yml')
        workflow = create_workflow(context.config)
        run(workflow, context)

        expected_vcl = np.array([0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 3, 3])

        self.assertTrue(np.array_equal(self.expected_vmain_shock,
                context.working_catalog))

        self.assertTrue(np.array_equal(expected_vcl, context.vcl))

        self.assertTrue(np.array_equal(self.expected_flag_vector,
                context.flag_vector))
