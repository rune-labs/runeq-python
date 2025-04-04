.. _resources:

Resources
=========

.. automodule:: runeq.resources

For example usage patterns, see :ref:`quickstart`.

API Clients
-----------

.. automodule:: runeq.resources.client

.. autofunction:: runeq.resources.client.initialize
.. autofunction:: runeq.resources.client.global_graph_client
.. autofunction:: runeq.resources.client.global_stream_client

.. autoclass:: runeq.resources.client.GraphClient
   :special-members: __init__
   :members:

.. autoclass:: runeq.resources.client.StreamClient
   :special-members: __init__
   :members:

Patient Metadata
----------------

.. automodule:: runeq.resources.patient

Patients
********

.. autofunction:: get_patient
.. autofunction:: get_all_patients

.. autoclass:: Patient
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: PatientSet
   :special-members: __init__
   :members:
   :inherited-members:


Devices
*******

.. autofunction:: get_device
.. autofunction:: get_all_devices

.. autoclass:: Device
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: DeviceSet
   :special-members: __init__
   :members:
   :inherited-members:

Organization Metadata
---------------------

.. automodule:: runeq.resources.org

.. autofunction:: get_org
.. autofunction:: get_orgs
.. autofunction:: set_active_org

.. autoclass:: Org
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: OrgSet
   :special-members: __init__
   :members:
   :inherited-members:

Stream Metadata
---------------

.. automodule:: runeq.resources.stream_metadata

.. autofunction:: get_all_stream_types
.. autofunction:: get_patient_stream_metadata
.. autofunction:: get_stream_availability_dataframe
.. autofunction:: get_stream_dataframe
.. autofunction:: get_stream_metadata

.. autoclass:: Dimension
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: StreamMetadata
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: StreamMetadataSet
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: StreamType
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: StreamTypeSet
   :special-members: __init__
   :members:
   :inherited-members:

Stream Data
-----------

.. automodule:: runeq.resources.stream

.. autofunction:: get_stream_availability
.. autofunction:: get_stream_data
.. autofunction:: get_stream_aggregate_window
.. autofunction:: get_stream_daily_aggregate


StrivePD Events
---------------

.. automodule:: runeq.resources.event

.. autofunction:: get_patient_events
.. autofunction:: get_patient_activity_events
.. autofunction:: get_patient_medication_events
.. autofunction:: get_patient_symptom_events
.. autofunction:: get_patient_wellbeing_events

.. autoclass:: Event
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: EventSet
   :special-members: __init__
   :members:
   :inherited-members:

Sleep Metrics
-------------

.. automodule:: runeq.resources.sleep

.. autofunction:: get_sleep_metrics

User Metadata
-------------

.. automodule:: runeq.resources.user

.. autofunction:: get_current_user

.. autoclass:: User
   :special-members: __init__
   :members:
   :inherited-members:

Project Metadata
----------------

.. automodule:: runeq.resources.project

Projects
********

.. autofunction:: get_projects
.. autofunction:: get_project
.. autofunction:: get_project_patients

.. autoclass:: Project
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: ProjectSet
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: ProjectPatientMetadata
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: ProjectPatientMetadataSet
   :special-members: __init__
   :members:
   :inherited-members:


Cohorts
********
.. autofunction:: get_cohort_patients

.. autoclass:: Cohort
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: CohortSet
   :special-members: __init__
   :members:
   :inherited-members:
