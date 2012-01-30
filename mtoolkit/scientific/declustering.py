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
* Afteran
* Reasenberg
"""

import numpy as np
import logging

from mtoolkit.scientific.catalogue_utilities import (decimal_year,
                                                        haversine,
                                                        greg2julian)


LOGGER = logging.getLogger('mt_logger')


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
              containing non-clustered events, **flagvector** indicating
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


def afteran_decluster(
    catalogue_matrix, window_opt='GardnerKnopoff', time_window=60.):
    '''AFTERAN declustering algorithm.
    ||(Musson, 1999, "Probabilistic Seismic Hazard Maps for the North Balkan
       region", Annali di Geofisica, 42(6), 1109 - 1124) ||
    :param catalog_matrix: eq catalog in a matrix format with these columns in
                            order: `year`, `month`, `day`, `longitude`,
                            `latitude`, `Mw`
    :type catalog_matrix: numpy.ndarray
    :keyword window_opt: method used in calculating distance and time windows
    :type window_opt: string
    :keyword time_window: Length (in days) of moving time window
    :type time_window: positive float
    :returns: **vcl vector** indicating cluster number, **vmain_shock catalog**
              containing non-clustered events, **flagvector** indicating
              which eq events belong to a cluster
    :rtype: numpy.ndarray
    '''

    #Convert time window from days to decimal years
    time_window = time_window / 365.

    # Pre-processing steps are the same as for Gardner & Knopoff
    # Get relevent parameters
    mag = catalogue_matrix[:, 5]

    neq = np.shape(catalogue_matrix)[0]  # Number of earthquakes
    # Get decimal year (needed for time windows)
    year_dec = decimal_year(catalogue_matrix[:, 0], catalogue_matrix[:, 1],
                            catalogue_matrix[:, 2])

    # Get space windows corresponding to each event
    sw_space = calc_windows(mag, window_opt)[0]

    eqid = np.arange(0, neq, 1)  # Initial Position Identifier

    # Pre-allocate cluster index vectors
    vcl = np.zeros((neq, 1), dtype=int)
    flagvector = np.zeros((neq, 1), dtype=int)
    # Sort magnitudes into descending order
    id0 = np.flipud(np.argsort(mag, kind='heapsort'))
    mag = mag[id0]
    catalogue_matrix = catalogue_matrix[id0, :]
    sw_space = sw_space[id0]
    year_dec = year_dec[id0]
    eqid = eqid[id0]

    i = 0
    clust_index = 0
    while i < neq:
        if vcl[i] == 0:
            # Earthquake not allocated to cluster - perform calculation
            # Perform distance calculation
            mdist = haversine(catalogue_matrix[:, 3], catalogue_matrix[:, 4],
                          catalogue_matrix[i, 3], catalogue_matrix[i, 4])

            # Select earthquakes inside distance window and not in cluster
            vsel = np.logical_and(mdist <= sw_space[i], vcl == 0).flatten()
            dtime = year_dec[vsel] - year_dec[i]

            nval = np.shape(dtime)[0]  # Number of events inside valid window
            # Pre-allocate boolean array (all True)
            vsel1 = np.array(np.ones(nval), dtype=bool)
            initval = dtime[0]  # Start with the mainshock
            # Search for aftershocks
            j = 1
            while j < nval:
                ddt = dtime[j] - initval
                # Is event after previous event and within time window?
                vsel1[j] = np.logical_and(ddt >= 0.0, ddt <= time_window)
                if vsel1[j]:
                    # Reset time window to new event time
                    initval = dtime[j]
                j += 1

            # Now search for foreshocks
            j = 1
            vsel2 = np.array(np.zeros(nval), dtype=bool)
            initval = dtime[0]
            while j < nval:
                if vsel1[j]:
                    # Event already allocated as an aftershock - skip
                    j += 1
                else:
                    ddt = dtime[j] - initval
                    # Is event before previous event and within time window?
                    vsel2[j] = np.logical_and(ddt <= 0.0,
                                              ddt >= -(time_window))
                    if vsel2[j]:
                        # Yes, reset time window to new event
                        initval = dtime[j]
                    j += 1
            temp_vsel = np.copy(vsel)
            temp_vsel[vsel] = np.logical_or(vsel1, vsel2)
            if np.shape(np.nonzero(temp_vsel)[0])[0] > 1:
                # Contains clustered events - allocate a cluster index
                vcl[temp_vsel] = clust_index + 1
                # Remove mainshock from cluster
                vsel1[0] = False
                # Assign markers to aftershocks and foreshocks
                temp_vsel = np.copy(vsel)
                temp_vsel[vsel] = vsel1
                flagvector[temp_vsel] = 1
                vsel[vsel] = vsel2
                flagvector[vsel] = -1
                clust_index += 1
        i += 1

    # Now have events - re-sort array back into chronological order
    # Re-sort the data into original order
    id1 = np.argsort(eqid, kind='heapsort')
    eqid = eqid[id1]
    catalogue_matrix = catalogue_matrix[id1, :]
    vcl = vcl[id1]
    flagvector = flagvector[id1]

    # Now to produce a catalogue with aftershocks purged
    vmain_shock = catalogue_matrix[np.nonzero(flagvector == 0)[0], :]

    return vcl.flatten(), vmain_shock, flagvector.flatten()


def fun_interact(mag, rfact):
    '''Reasenberg algorithm dependency to calculate interaction distances
    for a set of magnitudes
    :param mag: Magnitude of the earthquake
    :type mag: numpy.ndarray
    :param rfact: Distance interaction scaling factor
    :type rfact: positive float
    :returns: **r_1 vector** scaled interaction radius, **rmain vector**
              unscaled interaction radius
    :rtype: numpy.ndarray
    '''
    rmain = 0.011 * (10.0 ** (0.4 * mag))
    r_1 = rfact * rmain
    return r_1, rmain


def fun_tau_calc(xk, mbg, k1, xmeff, bgdiff, plev):
    '''Reasenberg algorithm dependenct to calculate look ahead time
    for clustered events
    :param xk:
    :type xk:
    :param mbg:
    :type mbg:
    :param k1:
    :type k1:
    :param xmeff:
    :type xmeff:
    :param bgdiff:
    :type bgdiff:
    :param plev:Probability (confidence) level
    :type plev: positive float
    :returns: **tau vector** Look ahead time for clustered events
    :rtype: numpy.ndarray
    '''
    deltam = (1 - xk) * mbg[k1] - xmeff
    if deltam < 0.:
        deltam = 0.
    tau = (10. ** ((deltam - 1.) * (2. / 3.))) / (-np.log(1. - plev) * bgdiff)
    return tau


def fun_time_diff(jj, ci, tau, clus, eqtime, neq):
    '''Reasenberg algorithm dependency to calculate time difference between
    the ith and jth event and return indices of events not already related
    to the cluster
    :param jj:
    :type jj:
    :param ci:
    :type ci:
    :param tau:
    :type tau:
    :param clus:
    :type clus:
    :param eqtime:
    :type eqtime:
    :param neq:
    :type neq:
    :returns:
    :rtype:
    '''
    tdiff = np.array([0.0])
    n = 0
    ac = np.array([], dtype='int32')
    while tdiff[n] < tau:
        # Time difference smaller than look-ahead time
        if jj <= neq:
            # To avoid problems when considering last event
            n = n + 1
            tdiff = np.vstack([tdiff, eqtime[jj] - eqtime[ci]])
            jj = jj + 1
        else:
            n = n + 1
            tdiff = np.vstack([tdiff, tau])
    k2 = clus[ci]

    jj = jj - 2
    if k2 != 0:
        if ci != jj:
            # Indices of EQs not already related to cluster k1
            ac = np.nonzero(clus[ci + 1: jj] != k2)[0] + ci
    else:
        if ci != jj:
            # No cluster is found already
            ac = np.arange(ci + 1, jj + 1, 1)
    return tdiff, ac


def fun_distance(i, bgevent, lon, lat, depth, ac, err, derr):
    '''Reasenberg algorithm dependency to calculate distance between two
    events - simultaneously for largest event in cluster and for the current
    event.
    :param i: Point to location of target event
    :type i: positive integer
    :param bgevent: Pointer to location of largest event in cluster
    :type bgevent: positive integer
    :param lon: Event longitude
    :type lon:numpy.ndarray
    :param lat: Event latitude
    :type lat: numpy.ndarray
    :param depth: Event Depth
    :type depth: numpy.ndarray
    :param ac:
    :type ac:
    :param err: Error in event epicentral location
    :type err: Positive float
    :param derr: Error in event depth (km)
    :type derr: Positive float
    '''
    pi2 = np.pi / 2.
    rad = np.pi / 180.
    flat = 0.993231

    alatr1 = lat[i] * rad
    alonr1 = lon[i] * rad
    alatr2 = lat[bgevent] * rad
    alonr2 = lon[bgevent] * rad
    blonr = lon[ac] * rad
    blatr = lat[ac] * rad

    tana = np.hstack([flat * np.tan(alatr1), flat * np.tan(alatr2)])
    geoa = np.arctan(tana)
    acol = pi2 - geoa
    tanb = flat * np.tan(blatr)
    geob = np.arctan(tanb)
    bcol = pi2 - geob
    diflon = np.column_stack([blonr - alonr1, blonr - alonr2])
    cosdel1 = (np.sin(acol[0]) * np.sin(bcol)) * np.cos(diflon[:, 0]) + \
               (np.cos(acol[0]) * np.cos(bcol))
    cosdel2 = (np.sin(acol[1]) * np.sin(bcol)) * np.cos(diflon[:, 1]) + \
               (np.cos(acol[1]) * np.cos(bcol))
    cosdel = np.column_stack([cosdel1, cosdel2])
    delr = np.arccos(cosdel)
    colat = pi2 - ((alatr1 + blatr) / 2.)
    colat = np.column_stack([colat, pi2 - ((alatr2 + blatr) / 2.)])
    radius = 6371.227 * (1. + (3.37853E-3) * ((1. / 3.) -
                         ((np.cos(colat)) ** 2.)))
    r = (delr * radius) - 1.5 * err[i]
    tmp1 = np.nonzero(r < 0.)[0]
    if np.shape(tmp1)[0] != 0:
        r[tmp1] = np.zeros((np.shape(tmp1)[0], 1))
    z = np.column_stack([np.abs(depth[ac] - depth[i]),
                         np.abs(depth[ac] - depth[bgevent])]) - derr[i]
    tmp2 = np.nonzero(z < 0.)[0]
    if np.shape(tmp2)[0] != 0:
        z[tmp2] = np.zeros((np.shape(tmp2)[0], 1))

    r = np.sqrt((z ** 2.) + (r ** 2.))
    dist1 = r[:, 0]
    dist2 = r[:, 1]
    return dist1, dist2


def reasenberg_decluster(catalogue_matrix, rfact=10., xmeff=1.5, xk=0.5,
               taumin=1., taumax=10., plev=0.95):
    '''Reasenberg (1985) Declustering Algorithm - re-coded from CORSSA
    implementation
    ||Reasenberg, P. A. (1985), "Second Order Moment of Central California
    Seismicity, 1969 - 1982". Journal of Geophysical Research. 90(B7),
    5479 - 5495||
    :param catalogue_matrix: Earthquake Catalogue - standard format
    :type catalogue_matrix: numpy.ndarray
    :keyword rfact: Interaction radius for dependent events (km)
    :type rfact: Positive float
    :keyword xmeff: Effective lower magnitude cut-off for the catalogue
    :type xmeff: Float
    :keyword xk: Factor to raise the lower magnitude within clustered
    :type xk: Positive float
    :keyword taumin: minimum look-ahead time for non clustered events
    :type taumin: Positive float
    :keyword taumax: maximum look ahead time for clustered events
    :type taumax: Positive float  >= taumin
    :keyword plev: Confidence Level for the next event in the sequence
    :type plev: Positive float in range 0.0 <= plev <= 1.0
    '''

    mag = catalogue_matrix[:, 5]
    neq = np.shape(catalogue_matrix)[0]

    # Calculate interaction radii
    r_1, rmain = fun_interact(mag, rfact)

    # Get indices of events with m >= 6
    limag = mag >= 6.0
    if np.sum(limag) == 0:
        limag = 0
    else:
        limag = np.nonzero(limag)[0]

    # Get earthquake time in Julian days - hour, minute & second
    # not used, so replace with zeros
    eqtime = greg2julian(catalogue_matrix[:, 0], catalogue_matrix[:, 1],
                         catalogue_matrix[:, 2], np.zeros(neq),
                         np.zeros(neq), np.zeros(neq))
    # Pre-allocate declustering output vector vcl
    vcl = np.zeros(neq, dtype='int32')
    kindex = 0
    ltn = neq - 1
    mbg = np.array([], dtype='float')
    bgevent = np.array([], dtype='int32')

    # Main declustering loop
    for i in range(0, ltn):
        j = i + 1
        k_1 = vcl[i]

        # Attach interaction time
        if k_1 != 0:
            # event i is already related to cluster
            if mag[i] > mbg[k_1 - 1]:
                # If the current magnitude is the biggest in cluster
                mbg[k_1 - 1] = mag[i]
                bgevent[k_1 - 1] = i
                tau = taumin
            else:
                bgdiff = eqtime[i] - eqtime[bgevent[k_1 - 1]]
                tau = fun_tau_calc(xk, mbg, k_1 - 1, xmeff, bgdiff, plev)
                if tau > taumax:
                    tau = taumax
                if tau < taumin:
                    tau = taumin
        else:
            tau = taumin
        # Extract earthquakes within interaction time window
        tdiff, a_c = fun_time_diff(j, i, tau, vcl, eqtime, neq)
        if np.shape(a_c)[0] != 0:
            # Some events qualify for further examination
            if k_1 != 0:
                # Event i is already related to a vclter
                tml = np.nonzero(vcl[a_c] != k_1)[0]
                if np.shape(tml)[0] != 0:
                    a_c = a_c[tml]

            rtest1 = r_1[i]
            if tau == taumin:
                rtest2 = 0.
            else:
                rtest2 = rmain[bgevent[k_1 - 1]]
            #Calculate distances from epicentre of the largest and
            # most recent earthquake
            if k_1 == 0:
                # THIS STILL NEEDS TO BE FIXED WITH NEW CATALOGUE LOCAIONS
                dist1, dist2 = fun_distance(i, i, catalogue_matrix[:, 10],
                                            catalogue_matrix[:, 11],
                                            catalogue_matrix[:, 15], a_c,
                                            catalogue_matrix[:, 12],
                                            catalogue_matrix[:, 16])
            else:
                dist1, dist2 = fun_distance(i, bgevent[k_1 - 1],
                                            catalogue_matrix[:, 10],
                                            catalogue_matrix[:, 11],
                                            catalogue_matrix[:, 15], a_c,
                                            catalogue_matrix[:, 12],
                                            catalogue_matrix[:, 16])

            # Extract earthquakes that fit the spatial interaction time
            sl0 = np.nonzero(np.logical_or(dist1 <= rtest1,
                                           dist2 <= rtest2))[0]

            if np.shape(sl0)[0] != 0:
                # Some earthquakes qualify for further examination
                l_l = a_c[sl0]   # EQs fit spatio-temporal criteria
                # EQs already assigned to a vclter
                lla = l_l[np.nonzero(vcl[l_l] != 0)[0]]
                # EQs not assigned to vclter
                llb = l_l[np.nonzero(vcl[l_l] == 0)[0]]
                if np.shape(lla)[0] != 0:
                    # Find the smallest cluster number -
                    # if several are possible
                    sl1 = np.min(vcl[lla])
                    if k_1 != 0:
                        k_1 = np.min(np.array([sl1, k_1]))
                    else:
                        k_1 = sl1

                    if vcl[i] == 0:
                        vcl[i] = k_1
                    # merge all related clusters together in the cluster
                    # with the smallest number
                    sl2 = lla[np.nonzero(vcl[lla] != k_1)[0]]
                    tempvar = np.hstack([i, sl2])
                    for j1 in tempvar:
                        if vcl[j1] != k_1:
                            sl5 = np.nonzero(vcl == vcl[j1])[0]
                            tm2 = np.shape(sl5)[0]
                            vcl[sl5] = k_1 * np.ones((tm2, 1))

                if k_1 == 0:
                    kindex = kindex + 1
                    k_1 = kindex
                    vcl[i] = k_1
                    mbg = np.hstack([mbg, mag[i]])
                    bgevent = np.hstack([bgevent, i])

                if np.shape(llb)[0] > 0:
                    vcl[llb] = k_1 * np.ones((np.shape(llb)[0], 1))

    # The array "vcl" should indicate which clustter each event belons to
    # 0 if not allocated to a cluster
    id0 = vcl == 0
    vmain_shock = catalogue_matrix[id0, :]
    flagvector = np.copy(vcl)
    flagvector[flagvector != 0] = 1

    return vcl, vmain_shock, flagvector
