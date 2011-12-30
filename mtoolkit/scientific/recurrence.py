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
which implement recurrence algorithms. Implemented
algorithms are:

* Recurrence analysis (Wiechart, MLE)
"""


import numpy as np


def recurrence_analysis(year_col, magnitude_col,
                        completeness_table, magnitude_window,
                        recurrence_algorithm, reference_magnitude,
                        time_window):
    """
    Recurrence algorithm

    :param year_col: catalog matrix year column
    :type year_col: numpy.ndarray
    :param magnitude_col: catalog matrix magnitude column
    :type magnitude_col: numpy.ndarray
    :param completeness_table: completeness table which represents
                               the earliest year at which the catalogue
                               is complete above a given magnitude
    :type completeness_table: numpy.ndarray
    :param magnitude_window: width of magnitude window
    :type magnitude_window: float
    :param recurrence_algorithm: recurrence algorithm could be one
                                 between Wiechart or MLE
    :type recurrence_algorithm: string
    :param reference_magnitude:
    :type reference_magnitude: float
    :param time_window: used only with Wiechart algorithm
    :type time_window: float
    :returns: bval computed bvalue, sigb , a_m computed avalue,
              siga_m
    :rtype: numpy.float64
    """

    if recurrence_algorithm == 'Wiechart':
        cent_mag, t_per, n_obs = wiechert_prep(
            year_col,
            magnitude_col,
            completeness_table[:, 0],
            completeness_table[:, 1],
            magnitude_window,
            time_window)

        bval, sigb, a_m, siga_m = wiechart(
            t_per,
            cent_mag,
            n_obs,
            reference_magnitude)
    else:

        bval, sigb, a_m, siga_m = b_maxlike_time(
                year_col,
                magnitude_col,
                completeness_table[:, 0],
                completeness_table[:, 1],
                magnitude_window,
                reference_magnitude)
    return bval, sigb, a_m, siga_m


def recurrence_table(mag, dmag, year):
    """
    Allows to count earthquake occurrences

    :param year: year of earthquake
    :type year:
    :param mag: magnitude
    :type mag:
    :param dmag:
    :type dmag: magnitude interval
    :returns:
    :rtype:
    """

    # Define magnitude vectors
    num_year = np.max(year) - np.min(year) + 1.
    upper_m = np.max(np.ceil(10.0 * mag) / 10.0)
    lower_m = np.min(np.floor(10.0 * mag) / 10.0)
    mag_range = np.arange(lower_m, upper_m + (2 * dmag), dmag)
    mval = mag_range[:-1] + (dmag / 2.0)
    # Find number of earthquakes inside range
    number_obs = np.histogram(mag, mag_range)[0]
    number_rows = np.shape(number_obs)[0]
    # Cumulative number of events
    n_c = np.zeros((number_rows, 1))
    i = 0
    while i < number_rows:
        n_c[i] = np.sum(number_obs[i:], axis=0)
        i += 1

    # Normalise to Annual Rate
    number_obs_annual = number_obs / num_year
    n_c_annual = n_c / num_year

    rec_table = np.column_stack([mval, number_obs, n_c, number_obs_annual,
                                 n_c_annual])

    return rec_table


def b_max_likelihood(mval, number_obs, dmag=0.1, m_c=0.0):
    """
    Allows to calculate avalue and bvalue by Maximum Likelihood

    :param mval:
    :type mval:
    :param number_obs:
    :type number_obs:
    :keyword dmag:
    :type dmag:
    :keyword m_c:
    :type m_c:
    :returns:
    :rtype:
    """

    # Exclude data below Mc
    id0 = mval >= m_c
    mval = mval[id0]
    number_obs = number_obs[id0]
    # Get Number of events, minimum magnitude and mean magnitude
    neq = np.sum(number_obs)
    m_min = np.min(mval)
    m_ave = np.sum(mval * number_obs) / neq
    # Calculate b-value
    bval = np.log10(np.exp(1.0)) / (m_ave - m_min + (dmag / 2.))
    # Calculate sigma b from Bender estimator
    sigma_b = np.sum(number_obs * ((mval - m_ave) ** 2.0)) / (neq * (neq - 1))
    sigma_b = 2.3 * (bval ** 2.0) * np.sqrt(sigma_b)
    return bval, sigma_b


def b_maxlike_time(year, mag, ctime, cmag, dmag, ref_mag=0.0):
    """
    Allows to get a profile of bvalue varying with time
    for calculation of the bvalue of the catalogue from MLE.
    The "final" bvalue is the weighted average of the various
    subsets - weighted according to the number of events in the subset

    :param year:
    :type year:
    :param mag:
    :type mag:
    :param ctime:
    :type ctime:
    :param cmag:
    :type cmag:
    :param dmag:
    :type dmag:
    :keyword ref_mag:
    :type ref_mag:
    :returns:
    :rtype:
    """

    ival = 0
    while ival < np.shape(ctime)[0]:
        id0 = np.abs(ctime - ctime[ival]) < 1E-5
        m_c = np.min(cmag[id0])
        # Find events later than cut-off year, and with magnitude
        # greater than or equal to the corresponding completeness magnitude
        id1 = np.logical_and(year >= ctime[ival], mag >= m_c)

        # Get a- and b- value for the selected events
        temp_rec_table = recurrence_table(mag[id1], dmag, year[id1])
        bval, sigma_b = b_max_likelihood(temp_rec_table[:, 0],
                                         temp_rec_table[:, 1], dmag, m_c)
        aval = np.log10(np.sum(id1)) + bval * ref_mag
        sigma_a = np.abs(np.log10(np.sum(id1)) +
                       (bval + sigma_b) * ref_mag - aval)
        if ival == 0:
            gr_pars = np.array([np.hstack([bval, sigma_b, aval, sigma_a])])
            neq = np.sum(id1)  # Number of events
        else:
            gr_pars = np.vstack([gr_pars, np.hstack([bval, sigma_b, aval,
                                                     sigma_a])])
            neq = np.hstack([neq, np.sum(id1)])
        ival = ival + np.sum(id0)

    # The nextapproach is to work out the average values of the G-R parameters
    # from these periods, weighted by the number of events in each period
    neq = neq.astype(float) / np.sum(neq)

    bval = np.sum(neq * gr_pars[:, 0])
    sigma_b = np.sum(neq * gr_pars[:, 1])
    aval = np.sum(neq * gr_pars[:, 2])
    sigma_a = np.sum(neq * gr_pars[:, 3])

    return bval, sigma_b, aval, sigma_a


def wiechert_prep(year, fmag, ctime, cmag, d_m, d_t):
    """
    Allows to prepare table input for Wiechart algorithm

    :param year: year from catalogue
    :type year:
    :param fmag: magnitude from catalogue
    :type fmag:
    :param ctime: time period of complteness interval (from completness output)
    :type ctime:
    :param cmag: completeness magnitude (from completeness output)
    :type cmag:
    :param d_m: magnitude bin size (config file)
    :type d_m:
    :param d_t: time bin size (from config file)
    :type d_t:
    :returns:
    :rtype:
    """

    # Check to make sure ctime and cmag are the same length
    if np.shape(ctime)[0] != np.shape(cmag)[0]:
        raise Exception(
        'Completeness time and magnitude intervals not compatible')

    # Use 2d histogram to get overall density.
    time_int = np.arange(np.min(year), np.max(year) + 1.5 * d_t, d_t)
    fmag = np.around(fmag, decimals=1)
    mag_int = np.arange(np.min(fmag), np.max(fmag) + 1.5 * d_m, d_m)
    fullcount1 = np.histogram2d(year, fmag,
                                bins=[time_int, mag_int])[0]
    # Now remove events below the completeness intervals
    n_y = np.shape(fullcount1)[1]
    cent_mag = (mag_int[:-1] + mag_int[1:]) / 2.
    n_int = np.shape(ctime)[0]
    i = 0

    while i < n_int:
        idx = np.nonzero(time_int < ctime[i])[0]
        idy = np.nonzero(mag_int < cmag[i])[0]
        if np.logical_or(np.shape(idx)[0] == 0, np.shape(idy)[0] == 0):
            i += 1
        else:
            fullcount1[:idx[-1], :idy[-1]] = 0
            i += 1
    n_obs = np.zeros(n_y)
    t_per = np.zeros(n_y)
    i = 0
    while i < n_y:
        # Count number of events in each magnitude bin
        n_obs[i] = np.sum(fullcount1[:, i])
        # corresponding year of completeness
        dummy1 = np.nonzero(cmag >= mag_int[i])[0]
        if np.shape(dummy1)[0] == 0:
            t_per[i] = np.max(year) - ctime[-1] + 1
        else:
            t_per[i] = np.max(year) - ctime[dummy1[0]] + 1
        i += 1

    return cent_mag, t_per, n_obs


def wiechart(tper, fmag, nobs, mrate=0, beta=1.5, itstab=1E-5):
    """
    Wiechart algorithm

    :param tper: length of observation period corresponding to magnitude
    :type tper:
    :param fmag: central magnitude
    :type fmag:
    :param nobs: number of events in magnitude increment
    :type nobs:
    :keyword mrate: target magnitude for rate
    :type mrate:
    :keyword beta: initial value for beta
    :type beta:
    :keyword itstab:
    :type itstab: stabilisation tolerance
    :returns:
    :rtype:
    """

    d_m = fmag[1] - fmag[0]
    itbreak = 0
    while (itbreak != 1):
        snm = np.sum(nobs * fmag)
        nkount = np.sum(nobs)
        tjexp = tper * np.exp(-beta * fmag)
        tmexp = tjexp * fmag
        sumexp = np.sum(np.exp(-beta * fmag))
        stmex = np.sum(tmexp)
        sumtex = np.sum(tjexp)
        stm2x = np.sum(fmag * tmexp)
        dldb = stmex / sumtex
        d2ldb2 = nkount * ((dldb ** 2.0) - (stm2x / sumtex))
        dldb = (dldb * nkount) - snm
        betl = np.copy(beta)
        beta = beta - (dldb / d2ldb2)
        sigbeta = np.sqrt(-1. / d2ldb2)
        bval = beta / np.log(10.0)
        sigb = sigbeta / np.log(10.)
        fngtm0 = nkount * (sumexp / sumtex)
        fn0 = fngtm0 * np.exp((-beta) * (fmag[0] - (d_m / 2.0)))
        stdfn0 = fn0 / np.sqrt(nkount)
        if np.abs(beta - betl) <= itstab:
            # Iteration has reached convergence
            if mrate == 0.:
                a_m = fngtm0
                siga_m = stdfn0
            else:
                a_m = fngtm0 * np.exp((-beta) * (mrate -
                                                (fmag[0] - (d_m / 2.0))))
                siga_m = a_m / np.sqrt(nkount)
            itbreak = 1
        else:
            continue
    return bval, sigb, a_m, siga_m
