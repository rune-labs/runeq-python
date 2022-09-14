.. _quickstart:

Quickstart
==========

Prerequisites
-------------

API Credentials
***************

To access Rune's APIs, you will need to obtain API credentials.
For multi-patient analyses, we recommended using **user access tokens**.
These provide access to all the user's allowed resources.

To create a new access token:

    1. Log in to the `Rune web portal <https://app.runelabs.io>`_
    2. Click on the profile icon, in the top right corner.
    3. Click on **User Settings**.
    4. On the left sidebar, click on **Access Tokens**.
    5. Click **CREATE ACCESS TOKEN**.
    6. Copy the token ID and secret *before closing the page*. The secret will never be shown again.

See :ref:`quickstart_config` for details about how to use these credentials
with this library.

It is highly recommended that you rotate your access tokens every 3-6 months,
by creating a new token and deactivating the old one. Store your access tokens
securely, and do not share them.

Multiple Organizations
**********************

For users who are members of multiple organizations, note that
user access tokens only operate within the context of the organization that
is **currently active**. To switch your active organization, log in to
the `Rune web portal <https://app.runelabs.io>`_ and click on the profile icon
in the top right corner. If you are a member of multiple organizations, the
profile icon's dropdown menu will have an option to switch your organization.

.. _quickstart_config:

Configuration Setup
-------------------

``runeq`` uses a `YAML <https://yaml.org/>`_-formatted file to manage configuration
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

Once a configuration file exists, you won't need to repeat this step (unless
you're rotating your access token, getting set up on a different computer, etc).

.. _quickstart_init:

Initialization
--------------

To get started with the library, use :class:`~runeq.initialize`:

.. code-block:: python

    from runeq import initialize

    initialize()

This loads credentials from your configuration file (see :ref:`quickstart_config`).

Usage
-----

Explore Metadata
****************

After initializing the library, you can fetch metadata about various resources.

For example, you can get information about your user, based on the authentication
credentials:

.. code-block:: python

    from runeq.resources.user import get_current_user

    my_user = get_current_user()
    print(my_user)


You can also fetch metadata about all the patients you have access to:

.. code-block:: python

    from runeq.resources.patient import get_all_patients

    patients = get_all_patients()

    for patient in patients:
        print('Code Name:\t', patient.code_name)
        print('Patient ID:\t', patient.id)
        print('Devices:')
        for device in patient.devices:
            print(' - Type: ', device.device_type_id)
            print('   Alias:', device.alias)
            print('   ID:   ', device.id)

        print('')


:class:`~runeq.resources.patient.get_all_patients` returns a :class:`~runeq.resources.patient.PatientSet`,
which can be serialized as a list of dictionaries, e.g. to save the metadata to a file:

.. code-block:: python

    import json

    with open('patients.json', 'w') as f:
        json.dump(patients.to_list(), f, indent=4)


You can also convert a :class:`~runeq.resources.patient.PatientSet` to a collection of
devices (a :class:`~runeq.resources.patient.DeviceSet`). This may be more convenient for
a columnar data format, like a `pandas <https://pandas.pydata.org/>`_ DataFrame.

.. code-block:: python

    import pandas as pd

    devices = patients.devices()
    devices_df = pd.DataFrame(devices.to_list())


Fetch Timeseries Data
*********************

Use :class:`~runeq.resources.stream_metadata.get_patient_stream_metadata` to get
a :class:`~runeq.resources.stream_metadata.StreamMetadataSet` with details about
a particular patient's data. If you're interested in a more specific set of streams,
the function accepts additional filters.

.. code-block:: python

    from runeq.resources.stream_metadata import get_patient_stream_metadata

    patient_id = "abc123"
    patient_streams = get_patient_stream_metadata(patient_id)

Once you have a :class:`~runeq.resources.stream_metadata.StreamMetadataSet`,
you can use the **filter** operation to get a more specific subset of streams:

.. code-block:: python

    # Filter for data collected from a particular device
    device_id = "eb#8c31"
    device_streams = patient_streams.filter(device_id=device_id)

    # Filter by broad category
    neural_streams = patient_streams.filter(category="neural")

    # Specify multiple arguments to find streams that match
    # all criteria
    neural_device_streams = patient_streams.filter(
        category="neural",
        device_id=device_id,
    )

    # Use a custom filter function
    import time

    def in_last_two_weeks(stream) -> bool:
        """Return True if stream has data in the last two weeks"""
        two_weeks_ago = time.time() - 14*24*60*60
        return stream.max_time > two_weeks_ago

    recent_vitals_streams = patient_streams.filter(
        category="vitals",
        filter_function=in_last_two_weeks
    )

Using a :class:`~runeq.resources.stream_metadata.StreamMetadataSet`,
you can fetch the **availability** of all or any of the streams:

.. code-block:: python

    availability_df = neural_device_streams.get_batch_availability_dataframe(
        start_time=166000000,
        end_time=1663123000,
        resolution=3600,
        batch_operation="any",
    )

When you're ready to fetch data, you can gather all the raw stream data into a
pandas dataframe:

.. code-block:: python

    stream_df = percept_mdkit_streams.get_stream_dataframe(
        start_time=1662499000,
        end_time=1663123000,
    )

You can also work directly with responses from the V2 Stream API. See
:class:`~runeq.resources.stream` and
:class:`~runeq.resources.stream_metadata.StreamMetadata` for details.
