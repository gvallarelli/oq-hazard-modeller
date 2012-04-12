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


class TrAttr(object):
    __slots__ = ('region_id msr smod dlr'.split())

    def __init__(self, region_id, msr, smod, dlr):
        self.check_msr_weight(msr, smod, dlr)
        self.check_msr(msr['model'])
        self.check_values(smod['value'], dlr['value'])
        self.check_weights(msr['weight'], smod['weight'], dlr['weight'])

        self.region_id = region_id
        self.msr = msr
        self.smod = smod
        self.dlr = dlr

    @classmethod
    def check_msr_weight(cls, msr, smod, dlr):
        if not len(msr['model']) == len(msr['weight']):
            raise ValueError('Each model shold have a corresponding weight')
        if not len(smod['value']) == len(smod['weight']):
            raise ValueError('Each value should have a corresponding weight')
        if not len(dlr['value']) == len(dlr['weight']):
            raise ValueError('Each value should have a corresponding weight')

    @classmethod
    def check_msr(cls, msr):
        for model in msr:
            if model not in SUPPORTED_MSR:
                raise ValueError(
                    'Magnitude Scaling Relation %s not supported' % model)

    @classmethod
    def check_values(cls, smod, dlr):
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


class ActiveShallowCrust(TrAttr):
    def __init__(self):
        super(ActiveShallowCrust, self).__init__(
            '001', DEFAULT_MSR,
            {'value': [30.0], 'weight': [1.0]}, DEFAULT_DLR)


class SubductionInterface(TrAttr):
    def __init__(self):
        super(SubductionInterface, self).__init__(
            '002', DEFAULT_MSR, SUBD_SMOD, DEFAULT_DLR)


class SubductionIntraslab(TrAttr):
    def __init__(self):
        super(SubductionIntraslab, self).__init__(
            '003', DEFAULT_MSR, SUBD_SMOD, DEFAULT_DLR)


class StableContinental(TrAttr):
    def __init__(self):
        super(StableContinental, self).__init__(
            '004', DEFAULT_MSR, VOL_STCON_SMOD,
            {'value': [1.0E-4], 'weight': [1.0]})


class Volcanic(TrAttr):
    def __init__(self):
        super(Volcanic, self).__init__(
            '005', DEFAULT_MSR, VOL_STCON_SMOD, DEFAULT_DLR)


class TectonicRegion(object):

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
        tr = None
        try:
            tr = TectonicRegion._region[type_name]
        except KeyError:
            raise ValueError('Invalid region type')
        return tr

    @staticmethod
    def create_tr(region_id, msr, smod, dlr):
        return TrAttr(region_id, msr, smod, dlr)
