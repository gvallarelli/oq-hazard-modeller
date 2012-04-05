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

from tests.helper import create_context, create_workflow, run


class MaximumMagnitudeTestCase(unittest.TestCase):

    def setUp(self):
        self.decimal_places = 5

    def test_maximum_magnitude_cum_moment(self):
        self.decimal_places = 1
        context = create_context('config_maxmag_cum_moment.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(6.6,
            sm.rupture_rate_model.truncated_gutenberg_richter.max_magnitude,
            self.decimal_places)

        self.assertAlmostEqual(0.1, sm.max_mag_sigma, self.decimal_places)

    def test_maximum_magnitude_kijko_npg(self):
        context = create_context('config_maxmag_kijko_npg.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(6.44347,
            sm.rupture_rate_model.truncated_gutenberg_richter.max_magnitude,
            self.decimal_places)

        self.assertAlmostEqual(0.10904, sm.max_mag_sigma, self.decimal_places)
