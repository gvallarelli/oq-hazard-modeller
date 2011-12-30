# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010-2011, GEM Foundation.
#
# MToolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# MToolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with MToolkit. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""
The purpose of this module is to provide functions
which implement declustering algorithms. Implemented
algorithms are:

* GardnerKnopoff
"""

import numpy as np
from mtoolkit.scientific.catalogue_utilities import decimal_year, haversine


def calc_windows(magnitude, window_opt):
    """
    Allows to calculate distance and time windows (sw, search window)
    see reference: `Van Stiphout et al (2010)`.

    :param magnitude: magnitude
    :type magnitude: float
    :param window_opt: window option can be one between: `Gruenthal`,
                       `Uhrhammer`, `GardnerKnopoff`
    :type window_opt: string
    :returns: distance and time windows
    :rtype: numpy.ndarray
    """

    if window_opt == 'Gruenthal':
        sw_space = np.exp(1.77 + np.sqrt(0.037 + 1.02 * magnitude))
        sw_time = np.abs(
            (np.exp(-3.95 + np.sqrt(0.62 + 17.32 * magnitude))) / 365.)
        sw_time[magnitude >= 6.5] = np.power(
            10, 2.8 + 0.024 * magnitude[magnitude >= 6.5]) / 365.

    elif window_opt == 'Uhrhammer':
        sw_space = np.exp(-1.024 + 0.804 * magnitude)
        sw_time = np.exp(-2.87 + 1.235 * magnitude / 365.)

    else:
        sw_space = np.power(10.0, 0.1238 * magnitude + 0.983)
        sw_time = np.power(10.0, 0.032 * magnitude + 2.7389) / 365.
        sw_time[magnitude < 6.5] = np.power(
            10.0, 0.5409 * magnitude[magnitude < 6.5] - 0.547) / 365.

    return sw_space, sw_time


def gardner_knopoff_decluster(
    catalog_matrix, window_opt='GardnerKnopoff', fs_time_prop=0):
    """
    Gardner Knopoff algorithm.

    :param catalog_matrix: eq catalog in a matrix format with these columns in
                            order: `year`, `month`, `day`, `longitude`,
                            `latitude`, `Mw`
    :type catalog_matrix: numpy.ndarray
    :keyword window_opt: method used in calculating distance and time windows
    :type window_opt: string
    :keyword fs_time_prop: foreshock time window as a proportion of
                           aftershock time window
    :type fs_time_prop: positive float
    :returns: **vcl vector** indicating cluster number, **vmain_shock catalog**
              containing non-clustered events, **flag_vector** indicating
              which eq events belong to a cluster
    :rtype: numpy.ndarray
    """

    # Get relevent parameters
    m = catalog_matrix[:, 5]
    neq = np.shape(catalog_matrix)[0]  # Number of earthquakes
    # Get decimal year (needed for time windows)
    year_dec = decimal_year(
        catalog_matrix[:, 0], catalog_matrix[:, 1], catalog_matrix[:, 2])
    # Get space and time windows corresponding to each event
    sw_space, sw_time = calc_windows(m, window_opt)
    eqid = np.arange(0, neq, 1)  # Initial Position Identifier

    # Pre-allocate cluster index vectors
    vcl = np.zeros(neq, dtype=int)

    # Sort magnitudes into descending order
    id0 = np.flipud(np.argsort(m, kind='heapsort'))
    m = m[id0]
    catalog_matrix = catalog_matrix[id0, :]
    sw_space = sw_space[id0]
    sw_time = sw_time[id0]
    year_dec = year_dec[id0]
    eqid = eqid[id0]
    #Begin cluster identification
    i = 0
    while i < neq:
        if vcl[i] == 0:
            # Find Events inside both fore- and aftershock time windows
            dt = year_dec - year_dec[i]
            ick = np.zeros(neq, dtype=int)
            vsel = np.logical_and(dt >= (-sw_time[i] * fs_time_prop),
                                              dt <= sw_time[i], vcl == 0)
            # Of those events inside time window, find those inside distance
            # window
            vsel1 = haversine(
                catalog_matrix[vsel, 3], catalog_matrix[vsel, 4],
                catalog_matrix[i, 3], catalog_matrix[i, 4]) <= sw_space[i]
            # Update logical array so that those events inside time window
            # but outside distance window are switched to False
            vsel[vsel] = vsel1
            # Allocate a cluster number
            vcl[vsel] = i + 1
            ick[vsel] = i + 1
            # Number of elements in cluster
            ick[i] = 0  # Remove mainshock from cluster
            # Indicate the foreshocks
            tempick = ick[vsel]
            id2 = year_dec[vsel] < year_dec[i]
            tempick[id2] = -1 * (i + 1)
            vcl[vsel] = tempick

            # vcl indicates the cluster to which an event belongs
            # +vcl = aftershock, -vcl = foreshock
            i += 1
        else:
            # Already allocated to cluster - skip event
            i += 1

    # Re-sort the catalog_matrix into original order
    id1 = np.argsort(eqid, kind='heapsort')
    eqid = eqid[id1]
    catalog_matrix = catalog_matrix[id1, :]
    vcl = vcl[id1]
    # Now to produce a catalogue with aftershocks purged
    vmain_shock = catalog_matrix[np.nonzero(vcl == 0)[0], :]
    # Also create a simple flag vector which, for each event, takes
    # a value of 1 if aftershock, -1 if foreshock, and 0 otherwise
    flagvector = np.copy(vcl)
    flagvector[vcl < 0] = -1
    flagvector[vcl > 0] = 1

    return vcl, vmain_shock, flagvector
