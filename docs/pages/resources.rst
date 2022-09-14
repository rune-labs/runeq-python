.. _resources:

Resources
=========

.. automodule:: runeq.resources

For example usage patterns, see :ref:`quickstart`.

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

.. autoclass:: Org
   :special-members: __init__
   :members:
   :inherited-members:
.. autoclass:: OrgSet
   :special-members: __init__
   :members:
   :inherited-members:

User Metadata
-------------

.. automodule:: runeq.resources.user

.. autofunction:: get_current_user

.. autoclass:: User
   :special-members: __init__
   :members:
   :inherited-members: