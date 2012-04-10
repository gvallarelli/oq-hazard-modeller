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

from mtoolkit.geo.simple_fault import SimpleFaultGeo


class SimpleFaultGeoTestCase(unittest.TestCase):

    def setUp(self):

        self.trace_fst_fault = [(90.563202328, 24.926468434),
            (90.510844525, 23.892401812), (90.615560132, 22.400204407),
            (90.995154209, 21.287601079)]

        self.trace_snd_fault = [(90.995154209, 21.287601079),
            (92.294781845, 19.714732881), (93.262975563, 18.352958814),
            (93.581460339, 17.816563619)]

        self.fst_fault = SimpleFaultGeo(self.trace_fst_fault, 4.0, 35.0, 5.0)

        self.snd_fault = SimpleFaultGeo(self.trace_snd_fault, 0.0, 35.0, 10.0)

    def test_sf_geo_length(self):
        self.assertAlmostEqual(411.14582,
            self.fst_fault.get_length(), places=5)
        self.assertAlmostEqual(472.08545,
            self.snd_fault.get_length(), places=5)

    def test_sf_geo_width(self):
        self.assertAlmostEqual(355.68511,
            self.fst_fault.get_width(), places=5)
        self.assertAlmostEqual(201.55697,
            self.snd_fault.get_width(), places=5)

    def test_sf_geo_area(self):
        self.assertAlmostEqual(146238.4464,
            self.fst_fault.get_area(), places=4)
        self.assertAlmostEqual(95152.1118,
            self.snd_fault.get_area(), places=4)
