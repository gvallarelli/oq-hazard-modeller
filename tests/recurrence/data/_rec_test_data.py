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

CATALOG_MATRIX = np.genfromtxt(
    'tests/maximum_magnitude/data/completeness_test_cat.csv',
    delimiter=',', skip_header=1)

REC_TABLE = np.genfromtxt(
    'tests/recurrence/data/recurrence_table_test_data1.csv', delimiter=',')

WEICHERT_PREP_TABLE =  np.genfromtxt(
    'tests/recurrence/data/weichert_prep_table_test_data1.csv', delimiter=',',
    skip_header=1)
