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
capable of serializing specific flavours
of the NRML data format.
"""

import os
from lxml import etree

from nrml import nrml_xml


class AreaSourceWriter(object):
    """
    AreaSourceWriter object allows to serialize a
    sequence of AreaSource objects in the nrml
    data format.
    """

    def __init__(self, filename):
        """
        Constructor
        :param filename: nrml input filename
        :type filename: string
        """

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            raise IOError('Dir %s not found' %
                (os.path.abspath(dirname), ))
        self.filename = filename

    def serialize(self, area_sources):
        """
        Write area source definitions in the nrml file
        :param area_sources: area source objects
        :type area_sources: sequence of area source objects
        """

        root_elem = _write_header(area_sources)
        root_elem = _write_body(root_elem, area_sources)

        tree = etree.ElementTree(root_elem)
        tree.write(open(self.filename, 'w'),
            xml_declaration=True, encoding='utf-8',
            pretty_print=True)


def _write_header(area_sources):
    """
    Create nrml header elems
    :param area_sources: area source objects
    :type area_sources: sequence of area source objects
    :returns: root elem with attached header elements
    :rtype: lxml.etree._Element
    """

    # Every area_source definition has header attributes
    first_area_source_index = 0
    root_elem = etree.Element(nrml_xml.ROOT, nsmap=nrml_xml.NSMAP)
    root_elem.attrib[nrml_xml.GML_ID] = \
        area_sources[first_area_source_index].nrml_id

    source_model_elem = etree.SubElement(
        root_elem, nrml_xml.SOURCE_MODEL)
    source_model_elem.attrib[nrml_xml.GML_ID] = \
        area_sources[first_area_source_index].source_model_id

    etree.SubElement(source_model_elem, nrml_xml.CONFIG)

    return root_elem


def _write_body(root_elem, area_sources):
    """
    Attach nrml body elements to the root element
    :param root_elem: root elem of nrml document
    :type root_elem: lxml.etree._Element
    :param area_sources: area source objects
    :type area_sources: sequence of area source objects
    :returns: root elem with attached body elements
    :rtype: lxml.etree._Element
    """

    source_model_elem = root_elem.find(nrml_xml.SOURCE_MODEL)
    for area_source in area_sources:
        source_model_elem.append(_area_source_elem(area_source))
    return root_elem


def _area_source_elem(area_source):
    """
    Create area source element by reading
    data from the area source object.
    :param area_source: area source object
    :type area_source: py:class:: AreaSource
    """

    area_source_elem = etree.Element(nrml_xml.AREA_SOURCE)
    area_source_elem.attrib[nrml_xml.GML_ID] = area_source.area_source_id

    name_elem = etree.SubElement(
        area_source_elem, nrml_xml.GML_NAME)
    name_elem.text = area_source.name

    tectonic_region_elem = etree.SubElement(
        area_source_elem, nrml_xml.TECTONIC_REGION)
    tectonic_region_elem.text = area_source.tectonic_region

    _write_area_boundary(area_source_elem, area_source.area_boundary)

    _write_rupture_rate_model(
        area_source_elem, area_source.rupture_rate_model)

    _write_rupture_depth_distrib(
        area_source_elem, area_source.rupture_depth_dist)

    hypocentral_depth_elem = etree.SubElement(
        area_source_elem, nrml_xml.HYPOCENTRAL_DEPTH)
    hypocentral_depth_elem.text = str(
        area_source.hypocentral_depth)

    return area_source_elem


def _write_area_boundary(container_elem, area_boundary):
    """
    Attach an area boundary element
    to the element container.
    :param container_elem: element which contains area boundary
    :type container_elem: lxml.etree._Element
    :param area_boundary: area boundary object
    :type area_boundary: py:class::AreaBoundary
    """

    area_boundary_elem = etree.SubElement(
        container_elem, nrml_xml.AREA_BOUNDARY)

    polygon_elem = etree.SubElement(
        area_boundary_elem, nrml_xml.POLYGON)

    exterior_elem = etree.SubElement(
        polygon_elem, nrml_xml.EXTERIOR)

    linear_ring_elem = etree.SubElement(
        exterior_elem, nrml_xml.LINEAR_RING)
    linear_ring_elem.attrib[nrml_xml.SRS_NAME] = area_boundary.srs_name

    pos_list_elem = etree.SubElement(
        linear_ring_elem, nrml_xml.POS_LIST)

    pos_list = []
    for point in area_boundary.pos_list:
        pos_list.append(point.lon)
        pos_list.append(point.lat)
    pos_list_elem.text = ' '.join(
        (str(value) for value in pos_list))


def _write_rupture_rate_model(container_elem,
    rupture_rate_model):
    """
    Attach a rupture rate model element
    to the element container.
    :param container_elem: element which contains rupture rate model
    :type container_elem: lxml.etree._Element
    :param rupture_rate_model: rupture rate model object
    :type rupture_rate_model: py:class::RuptureRateModel
    """

    rupture_rate_model_elem = etree.SubElement(
        container_elem, nrml_xml.RUPTURE_RATE_MODEL)

    _write_truncated_guten_richter(rupture_rate_model_elem,
            rupture_rate_model.truncated_gutenberg_richter)

    strike_elem = etree.SubElement(
            rupture_rate_model_elem, nrml_xml.STRIKE)
    strike_elem.text = str(rupture_rate_model.strike)

    dip_elem = etree.SubElement(
            rupture_rate_model_elem, nrml_xml.DIP)
    dip_elem.text = str(rupture_rate_model.dip)

    rake_elem = etree.SubElement(
            rupture_rate_model_elem, nrml_xml.RAKE)
    rake_elem.text = str(rupture_rate_model.rake)


def _write_truncated_guten_richter(container_elem,
    truncated_gutenberg_richter):
    """
    Attach a truncated gutenberg richter element
    to the element container.
    :param container_elem: element which contains truncated
     gutenberg richter
    :type container_elem: lxml.etree._Element
    :param truncated_gutenberg_richter: truncated_gutenberg richter object
    :type truncated_gutenberg_richter: py:class::TruncatedGutenRichter
    """

    truncatd_gutenberg_rich_elem = etree.SubElement(
        container_elem, nrml_xml.TRUNCATED_GUTEN_RICHTER)
    truncatd_gutenberg_rich_elem.attrib[nrml_xml.TYPE] = \
        truncated_gutenberg_richter.type_tgr

    a_value_elem = etree.SubElement(
        truncatd_gutenberg_rich_elem, nrml_xml.A_VALUE_CUMULATIVE)
    a_value_elem.text = \
        str(truncated_gutenberg_richter.a_value)
    b_value_elem = etree.SubElement(
        truncatd_gutenberg_rich_elem, nrml_xml.B_VALUE)
    b_value_elem.text = \
        str(truncated_gutenberg_richter.b_value)

    min_magnitude_elem = etree.SubElement(
        truncatd_gutenberg_rich_elem, nrml_xml.MIN_MAGNITUDE)
    min_magnitude_elem.text = \
        str(truncated_gutenberg_richter.min_magnitude)

    max_magnitude_elem = etree.SubElement(
        truncatd_gutenberg_rich_elem, nrml_xml.MAX_MAGNITUDE)
    max_magnitude_elem.text = \
        str(truncated_gutenberg_richter.max_magnitude)


def _write_rupture_depth_distrib(container_elem,
    rupture_depth_dist):
    """
    Attach a rupture depth distribution element
    to the element container.
    :param container_elem: element which contains rupture depth
     distribution
    :type container_elem: lxml.etree._Element
    :param rupture_depth_dist: rupture depth distribution object
    :type rupture_depth_dist: py:class::RuptureDepthDistrib
    """

    rupture_depth_distrib_elem = etree.SubElement(
        container_elem, nrml_xml.RUPTURE_DEPTH_DISTRIB)

    magnitude_elem = etree.SubElement(
        rupture_depth_distrib_elem, nrml_xml.MAGNITUDE)
    magnitude_elem.attrib[nrml_xml.TYPE] = \
        rupture_depth_dist.magnitude.type_mag
    magnitude_elem.text = ' '.join(
        (str(value) for value in
            rupture_depth_dist.magnitude.values))

    depth_elem = etree.SubElement(
        rupture_depth_distrib_elem, nrml_xml.DEPTH)
    depth_elem.text = ' '.join(
        (str(value) for value in
            rupture_depth_dist.depth))
