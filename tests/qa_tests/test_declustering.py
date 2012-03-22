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

        expected_vcl = np.array([0, 0, 0, 2, 2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 3, 3])

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
