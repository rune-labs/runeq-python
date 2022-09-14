.. _stream:

V1 Stream API
=============

The :class:`~runeq.stream` module contains classes that fetch timeseries data using
`V1 Stream API <https://docs.runelabs.io/stream/index.html>`_.


The V1 API is supported, but is not longer under active development. We recommend
using the :class:`~runeq.resources` module instead, which provides access to data from the
`V2 Stream API <https://docs.runelabs.io/stream/v2/index.html>`_.

Usage
-----

Initialization
**************

The global initialization method, as described in the Quickstart (:ref:`quickstart_init`),
does NOT apply to requests made by the :class:`~runeq.stream` module.

Start by creating a :class:`~runeq.stream.V1Client`, using a :class:`~runeq.config.Config`.
The configuration class uses the file that was created via the command line tool (see
:ref:`quickstart_config`).

.. code-block:: python

    from runeq import Config, stream

    cfg = Config()
    v1client = stream.V1Client(cfg)

Methods on the :class:`~runeq.stream.V1Client` are used to create **accessors** for each
type of data that can be queried using the V1 Stream API (e.g. accelerometry, events, local
field potentials, etc).

The example below initializes an :class:`~runeq.stream.v1.Accel` class, which will allow us
to fetch accelerometry data:

.. code-block:: python

    accel = v1client.Accel(
        patient_id='992967a09cad48378f7b628aff5bdf6c',
        device_id='ABCDEF',
        start_time=1562482800,
        end_time=1563692400,
    )

Accessors can be initialized with default query parameters, which will be used for all API requests.

JSON Endpoints
**************

An accessor can be used to iterate over paginated data from the respective JSON endpoint:

.. code-block:: python

    for result in accel.iter_json_data():
         print(result.keys())


To override the default query parameters, use keyword arguments:

.. code-block:: python

    for text in accel.iter_json_data(device_id='patient-ABC,device-456'):
        pass  # do something


CSV Endpoints
*************

An accessor can also iterate over paginated data from the respective CSV endpoint.

Here, we use the accessor to build up a `pandas <https://pandas.pydata.org/>`_ DataFrame,
containing the complete result set.

.. code-block:: python

    import io
    import pandas as pd

    df = pd.DataFrame()
    for text in accel.iter_csv_text():
        page_df = pd.read_csv(io.StringIO(text))
        df.append(page_df)


We can also iterate over each point from the CSV response. Each line from the CSV
is returned as a dict:

.. code-block:: python

    for point in accel.points():
        print(point)

    # the accessor itself is also an iterator
    for point in accel:
        print(point)

To override the default query parameters, use keyword arguments:

.. code-block:: python

    for point in accel.points(end_time=1563692400):
        pass  # do something

    for text in accel.iter_csv_text(device_id='patient-ABC,device-456'):
        pass  # do something

    # etc

Note that CSV-formatted data is not supported for all resources: refer to the
`API documentation <https://docs.runelabs.io/stream/index.html>`_ for details.

V1Client
--------

.. automodule:: runeq.stream
.. autoclass:: V1Client
   :members:

Accessors
---------

.. automodule:: runeq.stream.v1
   :noindex:

Each resource that is exposed by the Stream API can be queried through
an accessor class.

Accel
*****

.. autoclass:: Accel
   :members:
   :inherited-members:

BandPower
*********

.. autoclass:: BandPower
   :members:
   :inherited-members:

Event
*****
.. autoclass:: Event
   :members:
   :inherited-members:

HeartRate
*********
.. autoclass:: HeartRate
   :members:
   :inherited-members:

LFP
***

.. autoclass:: LFP
   :members:
   :inherited-members:

ProbabilitySymptom
******************

.. autoclass:: ProbabilitySymptom
   :members:
   :inherited-members:

Rotation
********

.. autoclass:: Rotation
   :members:
   :inherited-members:

Span
****

.. autoclass:: Span
   :members:
   :inherited-members:

State
*****

.. autoclass:: State
   :members:
   :inherited-members:
