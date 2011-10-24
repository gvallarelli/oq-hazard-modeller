# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010-2011, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with OpenQuake. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
The purpose of this module is to provide functions
which tackle specific job.
"""

import yaml
import numpy as np

from mtoolkit.eqcatalog import EqEntryReader
from mtoolkit.declustering import  gardner_knopoff_decluster


def load_config_file(context):
    """Load configuration options from config file"""

    config_file = open(context['config_filename'], 'r')
    context['config'] = yaml.load(config_file)


def read_eq_catalog(context):
    """Create eq entries by reading an eq catalog"""

    reader = EqEntryReader(context['config']['eq_catalog_file'])
    eq_entries = []
    for eq_entry in reader.read():
        eq_entries.append(eq_entry)
    context['eq_catalog'] = eq_entries


def apply_declustering(context):
    """Apply declustering algorithm to the eq catalog"""

    matrix = []
    attributes = ['year', 'month', 'day', 'longitude', 'latitude', 'Mw']
    for eq_entry in context['eq_catalog']:
        matrix.append([eq_entry[attribute] for attribute in attributes])
    numpy_matrix = np.array(matrix)
    vcl, vmain_shock, flag_vector = gardner_knopoff_decluster(numpy_matrix)

    context['vcl'] = vcl
    context['vmain_shock'] = vmain_shock
    context['flag_vector'] = flag_vector
