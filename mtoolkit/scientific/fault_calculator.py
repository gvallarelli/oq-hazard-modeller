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
"""
Module :mod:`mtoolkit.scientific.fault_calculator`
defines functions :function:`get_mfd`.
"""

import numpy as np

from nhlib.scalerel.wc1994 import WC1994

MOMENT_SCALING = (16.05, 1.5)


def get_mfd(slip, aseismic_coef, tectonic_region, sf_geo, b_value,
            min_mag, bin_width, max_mag=None, rake=None,
            moment_scaling=MOMENT_SCALING):
    """
    Calculates activity rate `Anderson & Luco (1983)` type one.
    If maximum magnitude (max_mag) is not provided, then it's
    computed by using the moment scaling relation (WC1994)
    and the rake.

    :param slip:
        Rate of slip (mm/yr) on the fault
    :param aseismic_coef:
        The proportion of the fault slip that is not `used` by earthquakes.
    :param tectonic_region:
        An instance of :class:`~mtoolkit.geo.tectonic_region.TectonicRegion`.
    :param sf_geo:
        An instance of :class:`~mtoolkit.geo.simple_fault.SimpleFaultGeo`.
    :param b_value:
        Ratio between smaller and larger earthquakes.
    :param min_mag:
        Minimum magnitude.
    :param bin_width:
        Magnitude interval.
    :keyword max_mag:
        Maximum magnitude.
    :keyword rake:
        Rake.
    :keyword moment_scaling:
        Moment scaling relation.
    :returns:
    """

    assert (slip > 0)
    assert (0.0 <= aseismic_coef <= 1.0)

    if max_mag == None:
        wc = WC1994()
        max_mag = wc.get_median_mag(sf_geo.get_area(), rake)

    occurrence_rate = []
    disp_length_ratio = tectonic_region.disp_length_ratio_first_value
    shear_mod = tectonic_region.shear_mod_first_value

    beta = np.sqrt(disp_length_ratio * (10.0 ** moment_scaling[0]) /
        ((shear_mod * 1.0E10) * (sf_geo.get_width() * 1E5)))

    dbar = moment_scaling[1] * np.log(10.0)
    bbar = b_value * np.log(10.0)
    mag = np.arange(min_mag - (bin_width / 2.),
            max_mag + (1.5 * bin_width), bin_width)

    seismic_slip = slip * (1.0 - aseismic_coef)
    cumulative_values = [_cumulative_value(seismic_slip, max_mag, m,
                         bbar, dbar, beta) for m in mag]
    for i, c in enumerate(cumulative_values[0:-2]):
        occurrence_rate.append(c - cumulative_values[i + 1])

    return occurrence_rate


def _cumulative_value(slip, mmax, mag_value, bbar, dbar, beta):
    """
    Calculate N(M > mag_value) using Anderson & Luco Type 1 formula
    Slip is input in mm/yr but needs to be converted to cm/yr - hence
    divide by 10.

    :param slip:
    :param mmax:
    :param mag_value:
    :param bbar:
    :param dbar:
    :param beta:
    """
    return (((dbar - bbar) / (bbar)) * ((slip / 10.) / beta) *
                np.exp(bbar * (mmax - mag_value)) *
                np.exp(-(dbar / 2.) * mmax))
