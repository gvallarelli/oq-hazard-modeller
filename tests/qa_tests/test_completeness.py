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


class CompletenessTestCase(unittest.TestCase):

    def test_stepp(self):
        context = create_context('config_stepp.yml')

        workflow = create_workflow(context.config)

        run(workflow, context)

        filtered_eq_events = np.array([
                    [1994., 4.0], [1994., 4.1], [1994., 4.2],
                    [1994., 4.3], [1994., 4.4], [1964., 4.5],
                    [1964., 4.6], [1964., 4.7], [1964., 4.8],
                    [1964., 4.9], [1964., 5.0], [1964., 5.1],
                    [1964., 5.2], [1964., 5.3], [1964., 5.4],
                    [1919., 5.5], [1919., 5.6], [1919., 5.7],
                    [1919., 5.8], [1919., 5.9], [1919., 6.0],
                    [1919., 6.1], [1919., 6.2], [1919., 6.3],
                    [1919., 6.4], [1919., 6.5], [1919., 6.6],
                    [1919., 6.7], [1919., 6.8], [1919., 6.9],
                    [1919., 7.0], [1919., 7.1], [1919., 7.2],
                    [1919., 7.3]])

        self.assertTrue(np.allclose(filtered_eq_events,
                context.completeness_table))
