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

from mtoolkit.scientific.recurrence import (recurrence_table,
    b_max_likelihood, b_maxlike_time, weichert_prep, weichert)

from tests.recurrence.data._rec_test_data import (CATALOG_MATRIX,
    REC_TABLE, WEICHERT_PREP_TABLE)


class RecurrenceTestCase(unittest.TestCase):

    def setUp(self):
        self.catalogue = CATALOG_MATRIX
        self.year = self.catalogue[:, 3]
        self.magnitude = self.catalogue[:, 17]
        self.ctime = np.array([1990., 1960., 1910.])
        self.cmag = np.array([4.0, 4.5, 5.0])
        self.dmag = None
        self.dtime = None
        self.rec_table = []

    def _generate_recurrence_table(self, dmagnitude, comp_index):
        self.dmag = dmagnitude
        unicorn = 1E-7
        index0 = np.logical_and(
            self.magnitude > (self.cmag[comp_index] - unicorn),
            self.year > (self.ctime[comp_index] - unicorn))
        rec_table = recurrence_table(self.magnitude[index0],
                                                     self.dmag,
                                                     self.year[index0])
        return rec_table

    def test_recurrence_table(self):
        expected_table = REC_TABLE
        self.dmag = 0.1
        self.assert_(np.allclose(expected_table,
            self._generate_recurrence_table(self.dmag, 1)))

    def test_b_max_likelihood(self):
        self.dmag = 0.1
        self.rec_table = self._generate_recurrence_table(0.1, 1)
        bvalue, sigmab = b_max_likelihood(self.rec_table[:, 0],
            self.rec_table[:, 1], self.dmag, np.min(self.rec_table[:, 0]))
        self.assertAlmostEqual(bvalue, 1.02823300686, places=5)
        self.assertAlmostEqual(sigmab, 0.03262690837, places=5)

    def test_b_maxlike_time(self):
        reference_magnitude = 4.0
        self.dmag = 0.1
        bval, sigbval, aval, sigaval = b_maxlike_time(
            self.year,
            self.magnitude,
            self.ctime,
            self.cmag,
            self.dmag,
            ref_mag = reference_magnitude)

        self.assertAlmostEqual(bval, 0.932427109817, places=5)
        self.assertAlmostEqual(sigbval, 0.0292987613655, places=5)
        self.assertAlmostEqual(aval, 22.0386166271, places=5)
        self.assertAlmostEqual(sigaval, 2.24138814935, places=5)

    def test_weichert_prep(self):
        self.dmag = 0.1
        self.dtime = 1.0
        weichert_test_data = WEICHERT_PREP_TABLE
        cent_mag, t_per, n_obs = weichert_prep(
            self.year,
            self.magnitude,
            self.ctime,
            self.cmag,
            self.dmag,
            self.dtime)
        self.assert_(np.allclose(cent_mag, weichert_test_data[:, 0]))
        self.assert_(np.allclose(t_per, weichert_test_data[:, 1]))
        self.assert_(np.allclose(n_obs.astype(float),
                                 weichert_test_data[:, 2]))

    def test_weichert(self):
        self.dmag = 0.1
        self.dtime = 1.0
        reference_magnitude = 4.0
        cent_mag, t_per, n_obs = weichert_prep(
            self.year,
            self.magnitude,
            self.ctime,
            self.cmag,
            self.dmag,
            self.dtime)
        bval, sigbval, aval, sigaval = weichert(t_per, cent_mag,
            n_obs, mrate = reference_magnitude)
        self.assertAlmostEqual(bval, 1.00385277747, places=5)
        self.assertAlmostEqual(sigbval, 0.0183577013014, places=5)
        self.assertAlmostEqual(aval,  46.6667993984, places=5)
        self.assertAlmostEqual(sigaval,  1.09964159678, places=5)
