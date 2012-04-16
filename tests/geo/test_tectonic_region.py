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
        asc = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.ACTIVE_SHALLOW_CRUST)
        sub_inter = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.SUBDUCTION_INTERFACE)
        sub_intra = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.SUBDUCTION_INTRASLAB)
        sc = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.STABLE_CONTINENTAL)
        vol = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.VOLCANIC)

        self.assertEqual(asc, ActiveShallowCrust())
        self.assertEqual(sub_inter, SubductionInterface())
        self.assertEqual(sub_intra, SubductionIntraslab())
        self.assertEqual(sc, StableContinental())
        self.assertEqual(vol, Volcanic())

    def test_given_an_incorrect_id_should_raise_value_ex(self):
        self.assertRaises(ValueError,
            self.tect_builder.create_tect_region_by_name, 'GRAEME CRUST')

    def test_given_inval_msr_weight_value_cardin_raise_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, None, None)

    def test_given_inval_smod_weight_value_cardin_raise_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7, 0.3]}
        smod = {'value': [4.5], 'weight': [5.0, 4.5]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, None)

    def test_given_inval_dlr_weight_value_cardin_raise_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7, 0.3]}
        smod = {'value': [4.5, 87.0], 'weight': [5.0, 4.5]}
        dlr = {'value': [4.5, 8.0, 87.0], 'weight': [5.0, 4.5]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_given_invalid_smod_weight_raise_value_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7, 0.3]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.6, 0.5]}
        dlr = {'value': [30], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_given_invalid_dlr_weight_raise_value_ex(self):
        msr = {'model': ['WC1994', 'Peer'], 'weight': [0.7, 0.3]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
        dlr = {'value': [30], 'weight': [6.0]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_given_unsupported_msr_raise_value_ex(self):
        msr = {'model': ['Graeme'], 'weight': [0.7]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
        dlr = {'value': [30], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_given_invalid_values_smod_dlr_raise_ex(self):
        msr = {'model': ['Peer'], 'weight': [1.0]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
        dlr = {'value': [-45], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_given_invalid_weights_raise_ex(self):
        msr = {'model': ['Peer'], 'weight': [1.0]}
        smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.1, 0.5]}
        dlr = {'value': [30], 'weight': [1.0]}

        self.assertRaises(ValueError, self.tect_builder.create_new_tect_region,
            None, msr, smod, dlr)

    def test_allow_construction_custom_tect_reg_by_name(self):
        customized_msr = {'model': ['Peer'], 'weight': [1.0]}
        customized_smod = {'value': [100.5, 40.0], 'weight': [0.6, 0.4]}
        customized_dlr = {'value': [50.0], 'weight': [1.0]}

        asc = ActiveShallowCrust()
        asc._msr = customized_msr
        asc_customized_msr = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.ACTIVE_SHALLOW_CRUST, msr=customized_msr)

        scon = StableContinental()
        scon._msr = customized_msr
        scon._smod = customized_smod
        scon._dlr = customized_dlr
        scon_customized_all = self.tect_builder.create_tect_region_by_name(
            TectonicRegionBuilder.STABLE_CONTINENTAL, msr=customized_msr,
            smod=customized_smod, dlr=customized_dlr)

        self.assertEqual(asc, asc_customized_msr)
        self.assertEqual(scon, scon_customized_all)
