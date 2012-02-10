.. _area_source:

Area Source Model
===============================================================================

For input into MToolkit, an area source must be implemented into the
corresponding nrml format. A full description of the nrml format for all the
currently supported seismogenic source typologies can be found inside the 
`OpenQuake user manual`_. The structure of the nrml definition for an area
source is described as follows:

Header tag
-------------------------------------------------------------------------------

.. code-block:: xml
   :linenos:

   <?xml version='1.0' encoding='utf-8'?>
   <nrml xmlns:gml="http://www.opengis.net/gml"
        xmlns="http://openquake.org/xmlns/nrml/0.3" gml:id="n1">
      <sourceModel gml:id="sm1">
      <config/>

Where *<sourceModel gml:id="sml">* assigns the code "sm1" to the whole source
model.

Area source tag
-------------------------------------------------------------------------------

Each individual area source is defined as follows:

.. code-block:: xml
   :linenos:

    <areaSource gml:id="src03">
        <gml:name>Quito</gml:name>
        <tectonicRegion>Active Shallow Crust</tectonicRegion>
        <areaBoundary>
          <gml:Polygon>
              <gml:exterior>
                  <gml:LinearRing srsName="urn:ogc:def:crs:EPSG::4326">
                      <gml:posList>-122.5 37.5 -121.5 37.5 -121.5 38.5 -122.5
                        38.5</gml:posList>
                  </gml:LinearRing>
              </gml:exterior>
          </gml:Polygon>
        </areaBoundary>
        <ruptureRateModel>
           <truncatedGutenbergRichter type="Mw">
               <aValueCumulative>5.0</aValueCumulative>
               <bValue>0.8</bValue>
               <minMagnitude>5.0</minMagnitude>
               <maxMagnitude>7.0</maxMagnitude>
           </truncatedGutenbergRichter>
           <strike>1.0</strike>
           <dip>90.0</dip>
           <rake>0.0</rake>
       </ruptureRateModel>
       <ruptureDepthDistribution>
           <magnitude type="ML">6.0 6.5 7.0</magnitude>
           <depth>5000.0 3000.0 0.0</depth>
       </ruptureDepthDistribution>
       <hypocentralDepth>5000.0</hypocentralDepth>
     </areaSource>


Each element in the above schema must contain a string, even if the required
values are not known. This is due to the schema validation checks that are
undertaken at the initiation of the workflow. Whilst the above describes the
complete model it is necessary to recognise that not all attributes can be
created by the MToolkit at this point. The version |version| workflow is designed
with the objective that for a set of area sources the calculation of the
*<truncatedGutenbergRichter>* parameters is  undertaken and the
*<aValueCumulative>*, *<bValue>*, *<minMagnitude>* (at present set by the
user in the configuration file) and *<maxMagnitude>* parameters are returned
for each source. If values of these parameters can be calculated inside the
MToolkit then the input values will be replaced with the calculated values.
If a recurrence calculation is not possible for a particular zone, as might
occur if the geographical filtering returns too few or no earthquakes, then a
warning message is returned to the user and the default values are **not**
overwritten. If implementing these results directly inside OpenQuake, then it
is preferable to default all the *<truncatedGutenbergRichter>* parameters to
0.0. Each source requires the definition of an identifier code ("src03" in the
example above), a name and an assigned tectonic region type. The delineation of
the area source with n vertices is given inside the *<gml:posList>* string:

.. code-block:: xml
   :linenos:

    <gml:posList>
        Long_1 Lat_1 Long_2 Lat_2 Long_3 Lat_3 ... Long_n Lat_n
    </gml:posList>

The *<strike>*, *<dip>* and *<rake>* attributes can be set according to the
user's interpretation of the predominant fault mechanism in the zone. If this
is not known then setting the values to 0.0, 90.0 and 0.0 respectively (i.e.
a North-South striking vertical strike-slip fault) would be the most
appropriate.

The *ruptureDepthDistribution*, if not specified, could be defaulted to
*<magnitude>6.0</magnitude>* and *<depth>5000.0</depth>* if not known.
Hypocentral depth may also take a default value of 5.000.

.. Links
.. _OpenQuake user manual: http://openquake.org/users/
