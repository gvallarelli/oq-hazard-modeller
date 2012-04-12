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

from mtoolkit.geo.tectonic_region import (TectonicRegion, DEFAULT_MSR,
    DEFAULT_DLR, VOL_STCON_SMOD)


class ATectonicRegionShould(unittest.TestCase):

    def setUp(self):
        self.tectreg = TectonicRegion()

    def test_given_the_id_return_the_corresponding_tr(self):
        asc = self.tectreg.create_default_tr(
            TectonicRegion.ACTIVE_SHALLOW_CRUST)

        self.assertEqual('001', asc.region_id)
        self.assertEqual(DEFAULT_MSR, asc.msr)
        self.assertEqual({'value': [30.0], 'weight': [1.0]}, asc.smod)
        self.assertEqual(DEFAULT_DLR, asc.dlr)

        vol = self.tectreg.create_default_tr(TectonicRegion.VOLCANIC)

        self.assertEqual('005', vol.region_id)
        self.assertEqual(DEFAULT_MSR, vol.msr)
        self.assertEqual(VOL_STCON_SMOD, vol.smod)
        self.assertEqual(DEFAULT_DLR, vol.dlr)
