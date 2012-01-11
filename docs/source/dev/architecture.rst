.. _architecture:

Architecture
===============================================================================

The MToolkit is a modular and simple software, it can be extended easily to
support :ref:`new hazard model development tools <contribute>`. This brief
chapter explains the key ideas behind his architecture.

A pipeline approach
-------------------------------------------------------------------------------

.. image:: ../img/MTpipeline.png

MToolkit's computation is organized in pipelines. The sequence of jobs inside
a pipeline reads and writes data to the context object. A job object acts
mainly as a wrapper to the scientific functions. An intermediate job inside
the pipeline can use the output produced by previous jobs, by reading data
in the context object and can write the results of his computation in the
context.



Two phases strategy
-------------------------------------------------------------------------------

.. image:: ../img/MtoolkitSetupPhase.png

.. image:: ../img/MtoolkitExecutionPhase.png

MToolkit's computation can be seen as a two phases strategy. In the first one
the configuration file is read and two pipelines are built by a PipeLineBuilder
object. The preprocessing pipeline is a sequence of jobs which apply some
transformations to the earthquake catalogue (e.g. declustering, completeness),
while the processing pipeline can be seen as a means to derive model parameters
for seisemic hazard calculations in Openquake.
The preprocessing and processing pipelines are used by a Workflow object which
is responsible about their *activation*. In the second phase the workflow
object activates the preprocessing pipeline and the processing one according to
an earthquake catalogue filtering strategy. The processing pipeline is run for
every source model. Every processing pipeline is independent and produces a new
complete source model, which expands the set of source models.
