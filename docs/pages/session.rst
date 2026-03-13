.. _session:

Session
=======

The :class:`~runeq.Session` object provides a session-based alternative to the
global :func:`~runeq.initialize` pattern. Instead of initializing global singleton
clients, you create a ``Session`` instance that holds its own API clients and
exposes all resource operations as namespaced methods.

This is useful when you need to:

- Work with multiple configurations (e.g. different organizations) in the same process
- Avoid global state for cleaner dependency management
- Use the SDK in applications where global singletons are undesirable

.. note::
    You should use **either** the global ``initialize()`` pattern **or** session-based
    clients, not both. If ``runeq`` has already been globally initialized when you
    create a ``Session``, a warning will be raised.

Getting Started
---------------

Create a :class:`~runeq.Config` and pass it to :class:`~runeq.Session`:

.. code-block:: python

    from runeq import Config, Session

    config = Config()
    session = Session(config)

All resource operations are available as namespaced methods on the session object:

.. code-block:: python

    # Organization metadata
    orgs = session.org.get_orgs()
    session.org.set_active_org(org_id)

    # Patient metadata
    patients = session.patient.get_all_patients()
    patient = session.patient.get_patient(patient_id)
    devices = session.patient.get_all_devices()

    # User metadata
    user = session.user.get_current_user()

    # Project metadata
    projects = session.project.get_projects()
    project_patients = session.project.get_project_patients(project_id)

    # Stream metadata and data
    stream_metadata = session.stream_metadata.get_patient_stream_metadata(patient_id)
    stream_df = session.stream_metadata.get_stream_dataframe(stream_ids, start_time=..., end_time=...)

    # Raw stream data
    data = session.stream.get_stream_data(stream_id, start_time=..., end_time=...)

    # Events
    events = session.event.get_patient_events(patient_id, start_time=..., end_time=...)

    # Sleep metrics
    from datetime import date
    sleep = session.sleep.get_sleep_metrics(patient_id, start_date=date(2025, 1, 1), end_date=date(2025, 1, 10))

Namespaces
----------

The session organizes methods into the following namespaces, each corresponding
to a resource module:

- ``session.org`` — Organization metadata (:mod:`~runeq.resources.org`)
- ``session.patient`` — Patient and device metadata (:mod:`~runeq.resources.patient`)
- ``session.project`` — Project and cohort metadata (:mod:`~runeq.resources.project`)
- ``session.user`` — User metadata (:mod:`~runeq.resources.user`)
- ``session.event`` — StrivePD events (:mod:`~runeq.resources.event`)
- ``session.stream_metadata`` — Stream metadata and dataframes (:mod:`~runeq.resources.stream_metadata`)
- ``session.stream`` — Raw stream data and availability (:mod:`~runeq.resources.stream`)
- ``session.sleep`` — Sleep metrics (:mod:`~runeq.resources.sleep`)

Each namespace method has the same signature as the corresponding module-level
function, minus the ``client`` parameter (which is provided by the session
automatically).

.. note::
    Object-level methods that make API calls (e.g.
    :meth:`~runeq.resources.stream_metadata.StreamMetadataSet.get_stream_dataframe`,
    :meth:`~runeq.resources.stream_metadata.StreamMetadataSet.get_batch_availability_dataframe`)
    are not yet supported in a session-based context. Use the corresponding
    namespace methods on the session instead.

API Reference
-------------

.. autoclass:: runeq.Session
   :special-members: __init__
   :members:
   :undoc-members:

OrgNamespace
~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.OrgNamespace
   :members:
   :undoc-members:

PatientNamespace
~~~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.PatientNamespace
   :members:
   :undoc-members:

ProjectNamespace
~~~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.ProjectNamespace
   :members:
   :undoc-members:

UserNamespace
~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.UserNamespace
   :members:
   :undoc-members:

EventNamespace
~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.EventNamespace
   :members:
   :undoc-members:

StreamMetadataNamespace
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.StreamMetadataNamespace
   :members:
   :undoc-members:

StreamNamespace
~~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.StreamNamespace
   :members:
   :undoc-members:

SleepNamespace
~~~~~~~~~~~~~~

.. autoclass:: runeq.resources.session.namespaces.SleepNamespace
   :members:
   :undoc-members:
