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
