.. _quickstart:

Quickstart
==========

Configuration
-------------

To start, create a :class:`~runeq.config.Config`, which holds credentials
and settings for accessing the API:

.. code-block:: python

    from runeq import Config

    cfg = Config('~/.rune/config.yaml')


In the example above, configuration was loaded from a `YAML <https://yaml.org/>`_-formatted
file. See the `example config <https://github.com/rune-labs/runeq-python/blob/master/example_config.yaml>`_
for the expected contents of this file.

If you are doing multi patient analysis it is recommended to use an access token
as this method of authentication will give you access to all patients in your org.


Stream API
----------

To access the `Stream API <https://docs.runelabs.io/stream/index.html>`_, create a
:class:`~runeq.stream.V1Client`, using a :class:`~runeq.config.Config`:

.. code-block:: python

    from runeq import stream

    v1client = stream.V1Client(cfg)

Methods on the :class:`~runeq.stream.V1Client` are used to create **accessors** for each type of data
that can be queried using the Stream API (e.g. accelerometry, events, local field potentials, etc).

The example below initializes an :class:`~runeq.stream.v1.Accel` class, which will allow us to
fetch accelerometry data:

.. code-block:: python

    accel = v1client.Accel(
        patient_id='patient-ABC',
        device_id='patient-ABC,device-123',
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
        page_df = pd.read_csv(io.StringIO(body))
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
