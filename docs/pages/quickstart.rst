.. _quickstart:

Quickstart
==========

Prerequisites
-------------

To access Rune's APIs, you will need to obtain API credentials.
For multi-patient analyses, we recommended using **access tokens**,
which provide access to all the patients in your organization.

For details about creating API credentials, refer to the
`Stream API documentation <https://docs.runelabs.io/stream/#section/Overview/Authentication>`_.


Configuration
-------------

``runeq`` uses `YAML <https://yaml.org/>`_-formatted files to manage configuration
settings (e.g. API credentials). The easiest way to set up this configuration is via
the ``runeq`` command line tool, which is installed along with the Python library.

To get started, open a terminal and run the following command in a Python environment
where ``runeq`` is installed. This command will prompt you to enter an access token ID
and secret, and it will create a configuration file in the default location.

.. code-block:: bash

    runeq configure setup


This command also provides options to get and set specific values in your config file. To
see help documentation:

.. code-block:: bash

    runeq configure --help


If you want to create or manage a configuration file manually, refer to the
`example config <https://github.com/rune-labs/runeq-python/blob/master/example_config.yaml>`_
for the expected contents.


Stream API
----------

To access the `Stream API <https://docs.runelabs.io/stream/index.html>`_, create a
:class:`~runeq.stream.V1Client`, using a :class:`~runeq.config.Config`. As shown below,
the configuration class uses the file that was created via the command line tool (see above).

.. code-block:: python

    from runeq import Config, stream

    cfg = Config()
    v1client = stream.V1Client(cfg)

Methods on the :class:`~runeq.stream.V1Client` are used to create **accessors** for each type of data
that can be queried using the Stream API (e.g. accelerometry, events, local field potentials, etc).

The example below initializes an :class:`~runeq.stream.v1.Accel` class, which will allow us to
fetch accelerometry data:

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
