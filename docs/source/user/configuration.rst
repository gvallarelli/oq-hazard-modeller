.. _configuration:

Configuration file
===============================================================================

Overview
-------------------------------------------------------------------------------

MToolkit configuration file is written in `yaml`_, it allows to define:

    1. Input files
    2. Output file
    3. The order of execution and type of preprocessing jobs to apply
    4. The order of execution and type of processing jobs to apply
    5. Parameters for preprocessing or processing jobs

MToolkit provides a sample configuration file that can be modified easily.
All the properties are specified as::
    
    property_name: value

Input/Output files
-------------------------------------------------------------------------------

MToolkit needs for its execution an earthquake catalogue in `csv` format and a
source model in the `Nrml`_ format, it's also important to specify where
results of computation should be stored. These values should be filled inside
the configuration file in:

.. code-block:: yaml
    :linenos:

    eq_catalog_file: path/to/input_catalogue.csv

    source_model_file: path/to/source_model.xml

    result_file: path/to/result_file.xml

Results are stored in a `nrml` document. MToolkit adds new information to the
starting source model document.

Sequence of preprocessing/processing jobs
-------------------------------------------------------------------------------

MToolkit needs at least a sequence of preprocessing jobs in order to be used,
a sequence of preprocessing jobs is defined as:

.. code-block:: yaml
    :linenos:
    
    preprocessing_jobs:
    - first_job
    - second_job

This sequence defines both the type of jobs that are going to be exexcuted and
the order of execution (*i.e. first_job, second_job*). Available jobs for a
preprocessing pipeline are:

    - GardnerKnopoff
    - Stepp

If no preprocessing jobs are required then this fields are left blank:

.. code-block:: yaml
    :linenos:

    preprocessing_jobs:


A pipeline for processing jobs is enabled by putting value true or yes to
apply_processing_jobs flag:

.. code-block:: yaml
    :linenos:

    apply_processing_jobs: yes
    
After enabling the processing pipeline is important to define the sequence of
processing jobs, in the same way as the previous sequence:

.. code-block:: yaml
    :linenos:
    
    processing_jobs:
    - first_job
    - second_job

Available jobs for processing pipeline are:

    - Recurrence


Job parameters
-------------------------------------------------------------------------------

The configuration file allows to detail job's parameters. In order to detail
is necessary to fill some values to defined properties as in the example
below:

.. code-block:: yaml
    :linenos:

    Stepp:
    {
        time_window: 5,

        magnitude_windows: 0.2,
  
        sensitivity: 0.1,
  
        increment_lock: True 
    } 


.. Links
.. _Yaml: http://www.yaml.org
.. _Nrml: http://docs.openquake.org/openquake/python/schema.html

