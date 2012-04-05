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

from mtoolkit.scientific.maximum_magnitude import (h_smooth,
    gauss_cdf_hastings, kijko_npg_intfunc_simps, exp_spaced_points,
    kijko_nonparametric_gauss, cumulative_moment, cum_mo_uncertainty)

from tests.maximum_magnitude.data._mmax_test_data import (CATALOG_MATRIX,
    SPACED_POINTS, GAUSS_CDF)


class MaxMagnitudeTestCase(unittest.TestCase):

    def setUp(self):
        self.catalogue = CATALOG_MATRIX
        self.year = self.catalogue[:, 3]
        self.magnitude = self.catalogue[:, 17]
        self.mag_sigma = self.catalogue[:, 18]

        # Select 100 largest events
        index100 = np.flipud(np.argsort(self.magnitude))
        index100 = index100[:100]
        self.mag_select = self.magnitude[index100]
        self.sigma_select = self.mag_sigma[index100]
        self.number_samples = 51.
        self.hfact = None
        self.dec_places = 5

    def test_h_smooth(self):
        self.hfact = h_smooth(self.mag_select)
        self.assertAlmostEqual(self.hfact, 0.11, self.dec_places)

    def test_exp_spaced_points(self):
        self.assert_(np.allclose(SPACED_POINTS,
            exp_spaced_points(5.8, 7.4, self.number_samples)))

    def test_gauss_cdf_hastings(self):
        test_array = np.arange(-3., 3.05, 0.05)
        expected_output = GAUSS_CDF
        self.assert_(np.allclose(expected_output,
                                 gauss_cdf_hastings(test_array, 0., 1.)))

    def test_kijko_npg_intfunc_simps(self):
        expected_points = exp_spaced_points(5.8, 7.4, 51.)
        self.hfact = h_smooth(self.mag_select)
        neq = np.float(np.shape(self.mag_select)[0])
        delta = kijko_npg_intfunc_simps(expected_points, self.mag_select,
                                             self.hfact, neq)
        self.assertAlmostEqual(delta, 0.0846108731604)

    def test_kijko_nonparametric_gauss(self):
        neq = np.float(np.shape(self.mag_select)[0])
        maxmag, sigmaxmag = kijko_nonparametric_gauss(self.mag_select,
            self.sigma_select, neq,
            self.number_samples, iteration_tolerance=0.01,
            maximum_iterations=1E3, max_observed=False)
        self.assertAlmostEqual(maxmag, 7.50754931102, self.dec_places)
        self.assertAlmostEqual(sigmaxmag, 0.146856577316, self.dec_places)

    def test_cumulative_moment(self):
        self.assertAlmostEqual(cumulative_moment(self.year,
                               self.magnitude), 7.4847336)

    def test_cum_mo_uncertainty(self):
        maxmag, sigmaxmag = cum_mo_uncertainty(self.year,
                                                    self.magnitude,
                                                    self.mag_sigma,
                                                    number_bootstraps=100,
                                                    seed=19820305)
        self.assertAlmostEqual(maxmag, 7.5234315, self.dec_places)
        self.assertAlmostEqual(sigmaxmag, 0.0525644, self.dec_places)
