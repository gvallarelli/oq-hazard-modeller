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
from mock import Mock
import numpy as np

from mtoolkit.catalog_filter import (AreaSourceCatalogFilter,
                                     SourceModelCatalogFilter)


class AreaSourceCatalogFilterTestCase(unittest.TestCase):

    def setUp(self):
        self.sm_geometry = {'area_boundary':
            [-0.5, 0.0, -0.5, 0.5, 0.0, 0.5, 0.0, 0.0]}
        self.empty_catalog = np.array([])

    def test_filtering_an_empty_eq_catalog(self):
        as_filter = AreaSourceCatalogFilter()
        self.assertTrue(np.allclose(
            self.empty_catalog,
            as_filter.filter_eqs(self.sm_geometry, self.empty_catalog)))

    def test_filtering_non_empty_eq_catalog(self):
        eq_internal_point = [2000, 1, 2, -0.25, 0.25]
        eq_side_point = [2000, 1, 2, -0.5, 0.25]
        eq_external_point = [2000, 1, 2, 0.5, 0.25]
        eq_catalog = np.array([eq_internal_point,
                eq_side_point, eq_external_point])

        as_filter = AreaSourceCatalogFilter()

        expected_catalog = np.array([eq_internal_point])
        self.assertTrue(np.array_equal(expected_catalog,
                as_filter.filter_eqs(self.sm_geometry, eq_catalog)))

    def test_a_bad_polygon_raises_exception(self):
        self.sm_geometry = {'area_boundary': [1, 1, 1, 2, 2, 1, 2, 2]}
        as_filter = AreaSourceCatalogFilter()

        self.assertRaises(RuntimeError,
            as_filter.filter_eqs, self.sm_geometry, self.empty_catalog)


class SourceModelCatalogFilterTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty_source_model(self):
        smodel_filter = SourceModelCatalogFilter(None)
        self.assertRaises(StopIteration, smodel_filter.filter_eqs([], []).next)

    def test_source_model_calling_a_filter(self):
        asource_filter = AreaSourceCatalogFilter()
        asource_filter.filter_eqs = Mock()
        asource_filter.filter_eqs.return_value = []

        smodel_filter = SourceModelCatalogFilter(asource_filter)

        smodel = smodel_filter.filter_eqs([dict(a=1), dict(b=2)], [])
        self.assertEqual((dict(a=1), []), smodel.next())
        self.assertEqual((dict(b=2), []), smodel.next())

        self.assertEqual(dict(a=1),
                asource_filter.filter_eqs.call_args_list[0][0][0])
        self.assertEqual(dict(b=2),
                asource_filter.filter_eqs.call_args_list[1][0][0])
