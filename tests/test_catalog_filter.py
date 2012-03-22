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
from mock import Mock
import numpy as np

from mtoolkit.catalog_filter import (SourceModelCatalogFilter,
                                     CatalogFilter,
                                     NullCatalogFilter)

from mtoolkit.source_model import AreaSource, AREA_BOUNDARY, POINT


def build_geometry(pos_list):

    area_source = AreaSource()
    area_source.area_boundary = AREA_BOUNDARY('fake',
        [POINT(pos_list[i], pos_list[i + 1])
                for i in xrange(0, len(pos_list), 2)])
    return area_source


class SourceModelCatalogFilterTestCase(unittest.TestCase):

    def setUp(self):

        self.sm_geometry = build_geometry([-0.5, 0.0, -0.5,
                            0.5, 0.0, 0.5, 0.0, 0.0])

        self.empty_catalog = np.array([])

    def test_filtering_an_empty_eq_catalog(self):
        sm_filter = SourceModelCatalogFilter()
        self.assertTrue(np.allclose(
            self.empty_catalog,
            sm_filter.filter_eqs(self.sm_geometry, self.empty_catalog)))

    def test_filtering_non_empty_eq_catalog(self):
        eq_internal_point = [2000, 1, 2, -0.25, 0.25]
        eq_side_point = [2000, 1, 2, -0.5, 0.25]
        eq_external_point = [2000, 1, 2, 0.5, 0.25]
        eq_catalog = np.array([eq_internal_point,
                eq_side_point, eq_external_point])

        sm_filter = SourceModelCatalogFilter()

        expected_catalog = np.array([eq_internal_point])
        self.assertTrue(np.array_equal(expected_catalog,
                sm_filter.filter_eqs(self.sm_geometry, eq_catalog)))

    def test_a_bad_polygon_raises_exception(self):
        self.sm_geometry = build_geometry([1, 1, 1, 2, 2, 1, 2, 2])
        sm_filter = SourceModelCatalogFilter()

        self.assertRaises(RuntimeError,
            sm_filter.filter_eqs, self.sm_geometry, self.empty_catalog)


class NullCatalogFilterTestCase(unittest.TestCase):

    def test_a_null_catalog_apply_no_filtering(self):

        eq_catalog = np.array([[2000, 1, 2, -0.25, 0.25]])
        null_filter = NullCatalogFilter()

        self.assertTrue(np.array_equal(eq_catalog,
                null_filter.filter_eqs(AreaSource(), eq_catalog)))


class CatalogFilterTestCase(unittest.TestCase):

    def test_empty_source_model(self):
        catalog_filter = CatalogFilter(None)
        self.assertRaises(StopIteration,
            catalog_filter.filter_eqs([], []).next)

    def test_source_model_calling_a_filter(self):
        sm_filter = SourceModelCatalogFilter()
        sm_filter.filter_eqs = Mock()
        sm_filter.filter_eqs.return_value = []

        catalog_filter = CatalogFilter(sm_filter)

        gen = catalog_filter.filter_eqs([dict(a=1), dict(b=2)], [])
        self.assertEqual((dict(a=1), []), gen.next())
        self.assertEqual((dict(b=2), []), gen.next())

        self.assertEqual(dict(a=1),
                sm_filter.filter_eqs.call_args_list[0][0][0])
        self.assertEqual(dict(b=2),
                sm_filter.filter_eqs.call_args_list[1][0][0])
