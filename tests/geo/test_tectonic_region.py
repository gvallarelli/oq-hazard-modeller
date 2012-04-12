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

from mtoolkit.geo.tectonic_region import (TectonicRegionBuilder,
    ActiveShallowCrust, SubductionInterface, SubductionIntraslab,
    StableContinental, Volcanic)


class ATectonicRegionShould(unittest.TestCase):

    def setUp(self):
        self.tect_builder = TectonicRegionBuilder()

    def test_given_the_id_return_the_corresponding_tr(self):
        asc = self.tect_builder.create_default_tr(
            TectonicRegionBuilder.ACTIVE_SHALLOW_CRUST)
        sub_inter = self.tect_builder.create_default_tr(
            TectonicRegionBuilder.SUBDUCTION_INTERFACE)
        sub_intra = self.tect_builder.create_default_tr(
            TectonicRegionBuilder.SUBDUCTION_INTRASLAB)
        sc = self.tect_builder.create_default_tr(
            TectonicRegionBuilder.STABLE_CONTINENTAL)
        vol = self.tect_builder.create_default_tr(
            TectonicRegionBuilder.VOLCANIC)

        self.assertEqual(asc, ActiveShallowCrust())
        self.assertEqual(sub_inter, SubductionInterface())
        self.assertEqual(sub_intra, SubductionIntraslab())
        self.assertEqual(sc, StableContinental())
        self.assertEqual(vol, Volcanic())

    def test_given_invalid_msr_model_weight_raise_value_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7]}
        self.assertRaises(ValueError, self.tect_builder.create_tr,
            None, msr, None, None)

    def test_given_unsupported_msr_raise_value_ex(self):
        msr = {'model': ['Graeme'], 'weight': [0.7]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
        dlr = {'value': [30], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_tr,
            None, msr, smod, dlr)

    def test_given_invalid_values_smod_dlr_raise_ex(self):
        msr = {'model': ['Peer'], 'weight': [1.0]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
        dlr = {'value': [-45], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_tr,
            None, msr, smod, dlr)

    def test_given_invalid_weights_raise_ex(self):
        msr = {'model': ['Peer'], 'weight': [1.0]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.1, 0.5]}
        dlr = {'value': [30], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_tr,
            None, msr, smod, dlr)
