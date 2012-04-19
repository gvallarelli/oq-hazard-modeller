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

import numpy as np

from nhlib.scalerel.wc1994 import WC1994

def get_mfd(slip, dlr, smod, fault_width, b_value,
            min_mag, bin_width, max_mag=None, rake=None,
            tectonic_region=None, sf_geo=None):

    print 'mmag %s' % max_mag
    if max_mag == None:
        wc = WC1994()
        max_mag = wc.get_median_mag(sf_geo.get_area(), rake)

    occurrence_rate = []
    moment_scaling = [16.05, 1.5]
    beta = np.sqrt((dlr * (10.0 ** moment_scaling[0])) / ((smod * 1.0E10) * (fault_width * 1E5)))
    dbar = moment_scaling[1] * np.log(10.0)
    bbar =  b_value * np.log(10.0)
    mag = np.arange(min_mag - (bin_width / 2.), max_mag + (1.5 * bin_width), bin_width)
    for ival in range(0, np.shape(mag)[0] - 2):
        occurrence_rate.append(
        _cumulative_value(slip, max_mag, mag[ival], bbar, dbar, beta) -
        _cumulative_value(slip, max_mag, mag[ival + 1], bbar, dbar, beta))

    return occurrence_rate

def _cumulative_value(slip, mmax, mag_value, bbar, dbar, beta):
    # Calculate N(M > mag_value) using Anderson & Luco Type 1 formula
    # Slip is input in mm/yr but needs to be converted to cm/yr - hence
    # divide by 10.
    return (((dbar - bbar) / (bbar)) * ((slip / 10.) / beta) *
                np.exp(bbar * (mmax - mag_value)) *
                np.exp(-(dbar / 2.) * mmax))
