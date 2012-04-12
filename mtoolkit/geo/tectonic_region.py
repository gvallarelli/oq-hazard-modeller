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
Module :mod:`mtoolkit.geo.tectonic_region` defines different tectonic
regions types.
"""


DEFAULT_MSR = {'model': ['WC1994'], 'weight': [1.0]}
DEFAULT_DLR = {'value': [1.25E-5], 'weight': [1.0]}
VOL_STCON_SMOD = {'value': [29.0], 'weight': [1.0]}
SUBD_SMOD = {'value': [49.0], 'weight': [1.0]}
SUPPORTED_MSR = ('Peer', 'WC1994')


class TectonicRegion(object):
    """
    Base class for tectonic region type.

    Subclasses define default values for:
    region id, magnitude scaling relation,
    shaer modulus and displacement length
    ratio.

    :param region_id:
        tectonic region identifier (literal).
    :param msr:
        magnitude scaling relations with associated weights.
    :type msr:
        dict with keys: 'model', 'weight' where at each key is associated
        a list of values.
    :param smod:
        shaer modulus values (in GPa [giga-pascals]) with associated weights.
    :type smod:
        dict with keys 'value', 'weight' where at each key is associated
        a list of values.
    :param dlr:
        displacement length ratio values with associated weights.
    :type dlr:
        dict with keys 'value', 'weight' where at each key is associated
        a list of values.
    """

    __slots__ = ('_region_id _msr _smod _dlr'.split())

    def __init__(self, region_id, msr, smod, dlr):
        self.check_msr_weight(msr, smod, dlr)
        self.check_msr(msr['model'])
        self.check_values(smod['value'], dlr['value'])
        self.check_weights(msr['weight'], smod['weight'], dlr['weight'])

        self._region_id = region_id
        self._msr = msr
        self._smod = smod
        self._dlr = dlr

    def __eq__(self, other):
        return (self._region_id == other._region_id and
                self._msr == other._msr and
                self._smod == other._smod and
                self._dlr == other._dlr)

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def check_msr_weight(cls, msr, smod, dlr):
        """
        Checks that every model of magnitude scaling relation
        has an associated weight.
        :raises ValueError:
            if not every model has an associated weight.
        """
        msg = 'Each model shold have a corresponding weight'

        if not len(msr['model']) == len(msr['weight']):
            raise ValueError(msg)
        if not len(smod['value']) == len(smod['weight']):
            raise ValueError(msg)
        if not len(dlr['value']) == len(dlr['weight']):
            raise ValueError(msg)

    @classmethod
    def check_msr(cls, msr):
        """
        Checks that the specified models of magnitude scaling relations
        are the ones.
        :raises ValueError:
            if a specified model is not supported.
        """
        for model in msr:
            if model not in SUPPORTED_MSR:
                raise ValueError(
                    'Magnitude Scaling Relation %s not supported' % model)

    @classmethod
    def check_values(cls, smod, dlr):
        """
        Checks that the values specified for the shaer modulus and the
        displacement length ratios are greater than zero.
        :raises ValueError:
            if a value is not greater than zero.
        """

        for value in smod:
            if not value > 0:
                raise ValueError(
                    'Shear Modulus values should be greater than zero')
        for value in dlr:
            if not value > 0:
                raise ValueError(
                    'Displacement Length Ratio values should be '
                    'greater than zero')

    @classmethod
    def check_weights(cls, msr, smod, dlr):
        """
        Checks that the sum of weights for magnitude scaling relation
        models, shaer modulus and displacement length ratio is equal to one.
        :raises ValueError:
            if the sum of values for one of msr, smod, dlr
            is not one.
        """

        sum_weights_msr = reduce(lambda x, y: x + y, msr)
        sum_weights_smod = reduce(lambda x, y: x + y, smod)
        sum_weights_dlr = reduce(lambda x, y: x + y, dlr)

        if sum_weights_msr != 1.0:
            raise ValueError('The sum of weights for magnitude scaling'
                            ' relations should be one')
        if sum_weights_smod != 1.0:
            raise ValueError('The sum of weights for shear modulus'
                           ' should be one')
        if sum_weights_dlr != 1.0:
            raise ValueError('The sum of weights for displacement length ratio'
                            ' should be one')


class ActiveShallowCrust(TectonicRegion):
    """
    Active shallow crust tectonic region.
    """
    def __init__(self):
        super(ActiveShallowCrust, self).__init__(
            '001', DEFAULT_MSR,
            {'value': [30.0], 'weight': [1.0]}, DEFAULT_DLR)


class SubductionInterface(TectonicRegion):
    """
    Subduction interface tectonic region.
    """
    def __init__(self):
        super(SubductionInterface, self).__init__(
            '002', DEFAULT_MSR, SUBD_SMOD, DEFAULT_DLR)


class SubductionIntraslab(TectonicRegion):
    """
    Subduction intraslab tectonic region.
    """
    def __init__(self):
        super(SubductionIntraslab, self).__init__(
            '003', DEFAULT_MSR, SUBD_SMOD, DEFAULT_DLR)


class StableContinental(TectonicRegion):
    """
    Stable continental tectonic region.
    """
    def __init__(self):
        super(StableContinental, self).__init__(
            '004', DEFAULT_MSR, VOL_STCON_SMOD,
            {'value': [1.0E-4], 'weight': [1.0]})


class Volcanic(TectonicRegion):
    """
    Volcanic tectonic region.
    """
    def __init__(self):
        super(Volcanic, self).__init__(
            '005', DEFAULT_MSR, VOL_STCON_SMOD, DEFAULT_DLR)


class TectonicRegionBuilder(object):
    """
    TectonicRegionBuilder builds tectonic region
    objects. It can create default tectonic regions
    (i.e. active shallow crust, subduction interface,
    subduction intraslab, stable continental, volcanic)
    or original ones by providing the needed parameters.

    >>> asc = TectonicRegionBuilder.create_default_tr(
    ...     TectonicRegionBuilder.ACTIVE_SHALLOW_CRUST)

    >>> region_id = '006'
    >>> msr = {'model': ['WC1994', 'Peer'], 'weight':[0.7, 0.3]}
    >>> smod = {'value': [0.2, 0.4, 0.5], 'weight': [0.2, 0.3, 0.5]}
    >>> dlr = {'value': [30], 'weight': [1.0]}
    >>> ntr = TectonicRegionBuilder.create_tr(region_id, msr, smod, dlr)
    """

    ACTIVE_SHALLOW_CRUST = 'Active Shallow Crust'
    SUBDUCTION_INTERFACE = 'Subduction Interface'
    SUBDUCTION_INTRASLAB = 'Subction Intraslab'
    STABLE_CONTINENTAL = 'Stable Continental'
    VOLCANIC = 'Volcanic'

    _region = {ACTIVE_SHALLOW_CRUST: ActiveShallowCrust(),
                SUBDUCTION_INTERFACE: SubductionInterface(),
                SUBDUCTION_INTRASLAB: SubductionIntraslab(),
                STABLE_CONTINENTAL: StableContinental(),
                VOLCANIC: Volcanic()}

    @staticmethod
    def create_default_tr(type_name):
        """
        Creates one of the default tectonic region.
        :raises ValueError:
            if the specified tectonic region name
            is not among the default ones.
        """

        tr = None
        try:
            tr = TectonicRegionBuilder._region[type_name]
        except KeyError:
            raise ValueError('Invalid region type')
        return tr

    @staticmethod
    def create_tr(region_id, msr, smod, dlr):
        """
        Creates an original tectonic region.
        """

        return TectonicRegion(region_id, msr, smod, dlr)
