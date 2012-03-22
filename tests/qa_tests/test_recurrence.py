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


class RecurrenceTestCase(unittest.TestCase):

    def setUp(self):
        self.decimal_places = 5

    def test_recurrence_weichert_algorithm(self):
        context = create_context('config_recurrence_weichert.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(
            sm.rupture_rate_model.truncated_gutenberg_richter.b_value,
            0.569790,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.recurrence_sigb,
            0.041210,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.rupture_rate_model.truncated_gutenberg_richter.a_value,
            132.051268,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.recurrence_siga_m,
            7.701386,
            self.decimal_places)

    def test_recurrence_mle_algorithm(self):
        context = create_context('config_recurrence_mle.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        sm = context.sm_definitions[0]

        self.assertAlmostEqual(
            sm.rupture_rate_model.truncated_gutenberg_richter.b_value,
            0.595256,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.recurrence_sigb,
            0.024816,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.rupture_rate_model.truncated_gutenberg_richter.a_value,
            158.109066,
            self.decimal_places)

        self.assertAlmostEqual(
            sm.recurrence_siga_m,
            49.997286,
            self.decimal_places)
