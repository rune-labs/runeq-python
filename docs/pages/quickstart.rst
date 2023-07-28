.. _quickstart:

Quickstart
==========

Prerequisites
-------------

API Credentials
***************

To access Rune's APIs, you will need to obtain API credentials.
For multi-patient analyses, we recommended using **user access tokens**.

.. note::
    If you belong to multiple organizations, note that only one organization is "active" at a time.
    You can only access resources that belong to your active organization. This impacts both what is
    returned by the SDK *and* what you see in the `Rune web portal <https://app.runelabs.io>`_.

    You can change your active organization through code (see :ref:`set_active_org`) or
    in the `Rune web portal <https://app.runelabs.io>`_ (click on the profile icon, in the top right corner).

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

.. _quickstart_config:

Configuration Setup
*******************

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

To get started with the library, use :class:`~runeq.initialize`. This loads credentials from your
configuration file (see :ref:`quickstart_config`).

.. code-block:: python

    from runeq import initialize

    initialize()

To see information about your authenticated user:

.. code-block:: python

    from runeq.resources.user import get_current_user

    my_user = get_current_user()
    print(my_user)
    print('Active Org:', my_user.active_org_name)

Usage
-----

.. _set_active_org:

Set Active Org
**************

To get metadata about all the organizations that you belong to:

.. code-block:: python

    from runeq.resources.org import get_orgs

    all_orgs = get_orgs()
    for org in all_orgs:
        print(org)

You can set your active organization using an org ID:

.. code-block:: python

    from runeq.resources.org import set_active_org

    org_id = "aa0c21f97d6a0593b0a247c68f015d68b787655e"
    active_org = set_active_org(org_id)
    print('Active Org:', active_org.name)


Explore Metadata
****************

After initializing the library, you can fetch metadata about various resources.

For example, you can fetch metadata about all the patients in your active org:

.. code-block:: python

    from runeq.resources.patient import get_all_patients

    patients = get_all_patients()

    for patient in patients:
        print(patient)
        for device in patient.devices:
            print(' ', device)

        print('')


:class:`~runeq.resources.patient.get_all_patients` returns a :class:`~runeq.resources.patient.PatientSet`.
This object can be serialized as a list of dictionaries, e.g. to save the metadata to a file:

.. code-block:: python

    import json

    with open('patients.json', 'w') as f:
        json.dump(patients.to_list(), f, indent=4)


You can also convert a :class:`~runeq.resources.patient.PatientSet` to a collection of
devices (a :class:`~runeq.resources.patient.DeviceSet`). This may be more convenient for
a columnar data format, like a `pandas <https://pandas.pydata.org/>`_ DataFrame.

.. code-block:: python

    import pandas as pd

    devices = patients.devices
    devices_df = pd.DataFrame(devices.to_list())

Similarly to fetching information about patients, you can fetch information about projects,
and metadata related to the patients within projects (and cohorts).

You can find information about a single project:

.. code-block:: python

    from runeq.resources.project import get_project

    project = get_project(project_id="example_id")
    print(project.to_dict())

To view all the patients in a project, and their related project metrics you can use the
following example:

.. code-block:: python

    from runeq.resources.project import get_project_patients

    project_patients = get_project_patients(project_id="example_id")

    for project_patient in project_patients:
        print(project_patient)
        for metric in project_patient.metrics:
            print(' ', metric)

        print('')

It may be easier to view a single project patient in a dataframe which you can do by:

.. code-block:: python

    from runeq.resources.project import get_project_patients

    project_patients = get_project_patients(project_id="example_id")
    target_patient_id = "patient_id_example"

    df = project_patients[target_patient_id].get_patient_metadata_dataframe()

    df


Fetch Timeseries Data
*********************

Use :class:`~runeq.resources.stream_metadata.get_patient_stream_metadata` to get
a :class:`~runeq.resources.stream_metadata.StreamMetadataSet` with details about
a particular patient's data. If you're interested in a more specific set of streams,
the function accepts additional filters.

.. code-block:: python

    from runeq.resources.stream_metadata import get_patient_stream_metadata

    patient_id = "c4bd060df1454aa0adc978985512c6e9"
    patient_streams = get_patient_stream_metadata(patient_id)
    print(f'Found {len(patient_streams)} streams')

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

You can also combine multiple :class:`~runeq.resources.stream_metadata.StreamMetadataSet` s, using **update**:

.. code-block:: python

    from runeq.resources.stream_metadata import StreamMetadataSet

    lfp_power_streams = patient_streams.filter(
        category="neural",
        measurement="lfp_trend_log_power",
    )
    tremor_streams = patient_streams.filter(
        category="symptom",
        measurement="tremor",
        stream_type_id="duration"
    )

    lfp_and_tremor_streams = StreamMetadataSet()
    lfp_and_tremor_streams.update(lfp_power_streams)
    lfp_and_tremor_streams.update(tremor_streams)

Using a :class:`~runeq.resources.stream_metadata.StreamMetadataSet`,
you can fetch the **availability** of all or any of the streams:

.. code-block:: python

    availability_df = lfp_and_tremor_streams.get_batch_availability_dataframe(
        start_time=1662000000,
        end_time=1663123000,
        resolution=3600,
        batch_operation="any",
    )

.. note::
    The API for "batch availability" has a limit on the number of streams
    that it can process at a time. If you're running the example code
    with a patient who has multiple devices, the snippet above may exceed
    the API limit. Try limiting the number of streams in the set using a custom
    filter function, to select for a few of those device IDs.

When you're ready to fetch data, you can gather all the raw stream data into a
pandas dataframe:

.. code-block:: python

    stream_df = lfp_and_tremor_streams.get_stream_dataframe(
        start_time=1662499000,
        end_time=1663123000,
    )

You can also work directly with responses from the V2 Stream API. See
:class:`~runeq.resources.stream` and
:class:`~runeq.resources.stream_metadata.StreamMetadata` for details.
