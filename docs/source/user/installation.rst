.. _installation:

Installation
===============================================================================

External Dependencies
-------------------------------------------------------------------------------
This part of the documentation covers the installation of MToolkit.
The first step is getting external dependencies properly installed.
MToolkit requires these libraries in order to be used:

* Lxml_ >= 2.3
* Numpy_ >= 1.6.1
* PyYaml_ >= 3.10
* Shapely_ >= 1.2.13

Installing these dependencis is simple with
`pip <http://www.pip-installer.org/>`_::

    $ pip install lxml

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install lxml

Get the code
-------------------------------------------------------------------------------

MToolkit is actively developed on GitHub, where the code is
`available <https://github.com/gem/mtoolkit>`_.

You can clone the public repository::

    git clone git@github.com:gem/mtoolkit.git

Or download the `zip <https://github.com/gem/mtoolkit/zipball/master>`_

Execute MToolkit
-------------------------------------------------------------------------------

Go inside MToolkit root directory::
    
    $ cd mtoolkit

Run MToolkit with::

    $ python main -i config.yml

All settings are defined in the :ref:`configuration file <configuration>`.


.. Links
.. _Lxml: http://lxml.de/
.. _Numpy: http://numpy.org/
.. _PyYaml: http://pyyaml.org/
.. _Shapely: https://github.com/sgillies/shapely

