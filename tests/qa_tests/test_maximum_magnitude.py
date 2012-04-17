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

from tests.helper import create_context, create_workflow, run


class MaximumMagnitudeTestCase(unittest.TestCase):

    def setUp(self):
        self.decimal_places = 5

    def test_maximum_magnitude_cum_moment(self):
        # It depends on a random seed so precision is relaxed
        self.decimal_places = 1
        context = create_context('config_maxmag_cum_moment.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(6.6,
            sm.rupture_rate_model.truncated_gutenberg_richter.max_magnitude,
            self.decimal_places)

        self.assertAlmostEqual(0.05, sm.max_mag_sigma, self.decimal_places)

    def test_maximum_magnitude_kijko_npg(self):
        context = create_context('config_maxmag_kijko_npg.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(6.44392,
            sm.rupture_rate_model.truncated_gutenberg_richter.max_magnitude,
            self.decimal_places)

        self.assertAlmostEqual(0.10922, sm.max_mag_sigma, self.decimal_places)
