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
The purpose of this module is to provide objects
capable of parsing specific flavours
of the NRML data format.
"""

from lxml import etree

from nrml import nrml_xml

from mtoolkit.source_model import (AreaSource, SimpleFaultSource, POINT,
    AREA_BOUNDARY, TRUNCATED_GUTEN_RICHTER, RUPTURE_RATE_MODEL, MAGNITUDE,
    RUPTURE_DEPTH_DISTRIB, EVENLY_DISC_MFD, FAULT_TRACE)

XML_NODE = 1


class NRMLReader(object):
    """
    NRMLReader object allows to parse source model
    in a nrml file in an iterative way. NRMLReader
    generates area source objects for each area
    source element in the parsed document.
    """

    def __init__(self, filename, schema):
        """
        Constructor
        :param filename: nrml input filename
        :type filename: string
        :param schema: nrml schema
        :type schema: string
        """

        self.filename = filename
        self.schema = etree.XMLSchema(etree.parse(schema))

        self.tag_action = {
            nrml_xml.AREA_SOURCE: _parse_area_source,
            nrml_xml.SIMPLE_FAULT_SOURCE: _parse_simple_fault_source,
            nrml_xml.COMPLEX_FAULT_SOURCE: _parse_complex_fault_source,
            nrml_xml.SIMPLE_POINT_SOURCE: _parse_simple_point_source}

    def read(self):
        """
        Generator method, yields AreaSource
        object for every area source element
        in the nrml input file.
        :returns: source model object
        :rtype: py:class:: AreaSource
        """

        with open(self.filename, 'rb') as nrml_file:
            for source_model in etree.iterparse(nrml_file, schema=self.schema):
                tag = source_model[XML_NODE].tag
                if tag in self.tag_action:
                    yield self.tag_action[tag](source_model[XML_NODE])


def _parse_area_source(as_elem):
    """
    Creates an AreaSource object by
    extracting data contained in an
    area source element.
    :param as_elem: area source element
    :type as_elem: lxml.etree._Element
    :returns: area source object
    :rtype: py:class::AreaSource
    """

    area_source = AreaSource()

    area_source.nrml_id = as_elem.getparent().getparent().get(
            nrml_xml.GML_ID)

    area_source.source_model_id = as_elem.getparent().get(
            nrml_xml.GML_ID)

    area_source.area_source_id = as_elem.get(
        nrml_xml.GML_ID)

    area_source.name = as_elem.find(
        nrml_xml.GML_NAME).text

    area_source.tectonic_region = as_elem.find(
        nrml_xml.TECTONIC_REGION).text

    area_source.area_boundary = _parse_area_boundary(
        as_elem.find(nrml_xml.AREA_BOUNDARY))

    area_source.rupture_rate_model = _parse_rupture_rate_model(
        as_elem.find(nrml_xml.RUPTURE_RATE_MODEL))

    area_source.rupture_depth_dist = _parse_rupture_depth_distrib(
        as_elem.find(nrml_xml.RUPTURE_DEPTH_DISTRIB))

    area_source.hypocentral_depth = float(as_elem.find(
        nrml_xml.HYPOCENTRAL_DEPTH).text)

    as_elem.clear()

    return area_source


def _parse_area_boundary(area_boundary_elem):
    """
    Creates an AreaBounday object by extracting
    data contained in an area boundary element.
    :param area_boundary_elem: area boundary element
    :type area_boundary_elem: lxml.etree._Element
    :returns: area boundary object
    :rtype: py:class::AreaBoundary
    """

    srs_name = area_boundary_elem.find('.//%s' %
        nrml_xml.LINEAR_RING).get(nrml_xml.LINEAR_RING_NAME)

    pos_list_values = area_boundary_elem.find(
        './/%s' % nrml_xml.POS_LIST).text.split()
    pos_list = [POINT(float(pos_list_values[i]), float(pos_list_values[i + 1]))
            for i in xrange(0, len(pos_list_values), 2)]

    area_boundary_elem.clear()

    return AREA_BOUNDARY(srs_name, pos_list)


def _parse_rupture_rate_model(rupture_rate_model_elem):
    """
    Creates a RuptureRateModel object by extracting
    data contained in an rupture rate model element.
    :param rupture_rate_model_elem: rupture rate model element
    :type rupture_rate_model: lxml.etree._Element
    :returns: rupture rate model object
    :rtype: py:class::RuptureRateModel
    """

    truncatd_gutenberg_rich_elem = rupture_rate_model_elem.find(
            nrml_xml.TRUNCATED_GUTEN_RICHTER)

    truncated_gutenberg_richter = TRUNCATED_GUTEN_RICHTER(
        float(truncatd_gutenberg_rich_elem.find(
            nrml_xml.A_VALUE_CUMULATIVE).text),
        float(truncatd_gutenberg_rich_elem.find(
            nrml_xml.B_VALUE).text),
        float(truncatd_gutenberg_rich_elem.find(
            nrml_xml.MIN_MAGNITUDE).text),
        float(truncatd_gutenberg_rich_elem.find(
            nrml_xml.MAX_MAGNITUDE).text),
        truncatd_gutenberg_rich_elem.get(nrml_xml.TYPE))

    rupture_rate_model = RUPTURE_RATE_MODEL(truncated_gutenberg_richter,
        float(rupture_rate_model_elem.find(nrml_xml.STRIKE).text),
        float(rupture_rate_model_elem.find(nrml_xml.DIP).text),
        float(rupture_rate_model_elem.find(nrml_xml.RAKE).text))

    truncatd_gutenberg_rich_elem.clear()
    rupture_rate_model_elem.clear()

    return rupture_rate_model


def _parse_rupture_depth_distrib(rdd_elem):
    """
    Creates a RuptureDepthDistrib object by extracting
    data contained in an rupture depth distribution
    element.
    :param rdd_elem: rupture depth distribution element
    :type rdd_elem: lxml.etree._Element
    :returns: rupture depth distribution object
    :rtype: py:class::RuptureDepthDistrib
    """

    magnitude_elem = rdd_elem.find(nrml_xml.MAGNITUDE)
    magnitude = MAGNITUDE(
            magnitude_elem.get(nrml_xml.TYPE),
            [float(value) for value in rdd_elem.find(
                    nrml_xml.MAGNITUDE).text.split()])

    rupture_depth_distrib = RUPTURE_DEPTH_DISTRIB(
            magnitude,
            [float(value) for value in rdd_elem.find(
            nrml_xml.DEPTH).text.split()])

    rdd_elem.clear()

    return rupture_depth_distrib


def _parse_simple_fault_source(sf_elem):
    """
    Creates an SimpleFaultSource object by
    extracting data contained in an
    simple fault source element.
    :param sf_elem: simple fault source element
    :type sf_elem: lxml.etree._Element
    :returns: simple fault source object
    :rtype: py:class::SimpleFaultSource
    """
    sf_source = SimpleFaultSource()

    sf_source.nrml_id = sf_elem.getparent().getparent().get(
            nrml_xml.GML_ID)

    sf_source.source_model_id = sf_elem.getparent().get(
            nrml_xml.GML_ID)

    sf_source.simple_fault_source_id = sf_elem.get(
        nrml_xml.GML_ID)

    sf_source.name = sf_elem.find(
        nrml_xml.GML_NAME).text

    sf_source.tectonic_region = sf_elem.find(
        nrml_xml.TECTONIC_REGION).text

    sf_source.rake = sf_elem.find(
        nrml_xml.RAKE).text

    geo_id = sf_elem.find(
        nrml_xml.SIMPLE_FAULT_GEOMETRY).get(nrml_xml.GML_ID)

    return sf_source



def _parse_complex_fault_source(cp_elem):
    pass

def _parse_simple_point_source(sp_elem):
    pass
