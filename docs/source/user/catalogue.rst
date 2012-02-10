.. _catalogue:

Earthquake catalogue
===============================================================================

The earthquake catalogue should be prepared in a csv format with columns
specified with this order, compulsory fields are bold in the description
below:

.. parsed-literal::

    eventID, Agency, Identifier, year, month,day, hour, minute, second,
    timeError, longitude, latitude, SemiMajor90, SemiMinor90, ErrorStrike,
    depth, depthError, Mw, sigmaMw, Ms, sigmaMs, mb, sigmamb, ML, sigmaML 

The attributes of the earthquake catalogue are described as follows, and
correspond to a relatively simplified description of an event based on the
International Seismological Centre's (ISC) `IMS 1.0 format`_.

- | **eventID**: A unique identifier (integer) for each earthquake in the
    catalogue

- | Agency: The code (string) of the recording agency for the event solution

- | Identifier: A secondary identifier (integer) not used at present

- | **Year**: Year of event (integer) in the range -10000 to present
    (events before common era (BCE) should have a negative value).

- **Month**: Month of event (integer)

- **Day**: Day of event (integer)

- **Hour**: Hour of event (integer) - if unknown then set to 0

- **Minute**: Minute of event (integer) - if unknown then set to 0

- **Second**: Second of event (float) - if unknown set to 0.0

- timeError: Error in event time (float)

- **longitude**: Longitude of event, in decimal degrees (float)

- **latitude**: Latitude of event, in decimal degrees (float)

- | SemiMajor90: Length (km) of the semi-major axis of the 90
    \% confidence ellipsoid for location error (float)

- | SemiMinor90: Length (km) of the semi-minor axis of the 90
    \% confidence ellipsoid for location error (float)

- | ErrorStrike: Azimuth (in degrees) of the 90
    \% confidence ellipsoid for location error (float)

- **depth**: Depth (km) of earthquake (float)

- | depthError: Uncertainty (as standard deviation)
    in earthquake depth (km) (float)

- **Mw**: Moment magnitude of event (float)

- | sigmaMw: Uncertainty (standard deviation) in moment magnitude
    of event (float)

- Ms: Surface-wave magnitude of event (float)

- | sigmaMs: Uncertainty (standard deviation) in surface-wave magnitude
    of event (float)

- mb: Body-wave magnitude of event (float)

- | sigmamb: Uncertainty (standard deviation) in body-wave magnitude of
    event (float)

- ML: Local magnitude of event (float)

- | sigmaML: Uncertainty (standard deviation) in local magnitude of
    event (float)

.. Links
.. _IMS 1.0 format: http://www.isc.ac.uk/search/bulletin/descrip.html
