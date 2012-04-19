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

from mtoolkit.scientific.fault_calculator import get_mfd

from mtoolkit.geo.tectonic_region import TectonicRegionBuilder
from mtoolkit.geo.simple_fault import SimpleFaultGeo


class AFaultCalculatorShould(unittest.TestCase):

    def setUp(self):
        pass

    def _input_args(self):
        return {
        'slip' : 20.0,
        'dlr' : 1.25E-5,
        'smod' : 27.7,
        'fault_width' : 355.685110616,
        'b_value' : 0.8,
        'min_mag' : 5.0,
        'bin_width' : 0.1,
        'max_mag' : 8.5
        }

    def test_calculate_occurance_rates(self):

        exp_occ_rates = [0.719905173075, 0.598791041594,
                         0.498052694858, 0.414262187683,
                         0.344568279453, 0.28659941152,
                         0.238383007322, 0.198278349137,
                         0.164920747406, 0.137175102795,
                         0.114097280802, 0.0949019845528,
                         0.0789360325568, 0.0656561321153,
                         0.0546103920443, 0.0454229456281,
                         0.0377811605502, 0.0314250005759,
                         0.0261381769859, 0.0217407886596,
                         0.0180832003622, 0.0150409509269,
                         0.0125105180639, 0.0104057956833,
                         0.00865516385886, 0.00719905173075,
                         0.00598791041594, 0.00498052694858,
                         0.00414262187683, 0.00344568279453,
                         0.0028659941152, 0.00238383007322,
                         0.00198278349137, 0.00164920747406,
                         0.00137175102795]

        a = get_mfd(**self._input_args())
        for i, x in enumerate(a):
            self.assertAlmostEqual(exp_occ_rates[i], a[i], places=5)

    def test_compute_max_mag_using_msr(self):
        args = self._input_args()
        args['max_mag'] = None
        args['rake'] = -90
        args['tectonic_region'] = TectonicRegionBuilder.create_tect_region_by_name(
                TectonicRegionBuilder.ACTIVE_SHALLOW_CRUST)


        args['sf_geo'] = SimpleFaultGeo([(90.5632, 24.9265), (90.5108, 23.8924), (90.6156, 22.4002), (90.9952, 21.2876)],
                                        4.00, 35.0, 5.0)

        exp_occ_rates = [0.780179383967, 0.648924946545, 0.539752260701, 0.448946375822,
                         0.373417330576, 0.310595007075, 0.258341674371, 0.214879245307,
                         0.178728771409, 0.148660116911, 0.123650099455, 0.10284767302,
                         0.08554496836, 0.071153205482, 0.0591826585177, 0.0492259912326,
                         0.0409443961039, 0.0340560653089, 0.0283266013102, 0.0235610407283,
                         0.0195972200873, 0.0163002576829, 0.0135579638003, 0.011277023099,
                         0.00937981925965, 0.00780179383967, 0.00648924946545, 0.00539752260701,
                         0.00448946375822, 0.00373417330576, 0.00310595007075, 0.00258341674371,
                         0.00214879245307, 0.00178728771409, 0.00148660116911, 0.00123650099455,
                         0.0010284767302, 0.0008554496836, 0.00071153205482, 0.000591826585177,
                         0.000492259912326, 0.000409443961039]

        a = get_mfd(**args)
        for i, x in enumerate(a):
            self.assertAlmostEqual(exp_occ_rates[i], a[i], places=5)


