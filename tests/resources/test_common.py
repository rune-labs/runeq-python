"""
Tests for the V2 SDK Common Classes.

"""
from typing import List, Type
from unittest import TestCase

from runeq.resources.common import ItemBase, ItemSet


class StreamItem(ItemBase):
    """
    Test ItemBase class that represents a Stream

    """

    def __init__(self, id: str, **attributes):
        """
        Initializes StreamItem

        """
        super().__init__(id=id, **attributes)

    @property
    def id(self) -> str:
        """
        ID of the Stream

        """
        return self._attributes.get("id")


class PatientItem(ItemBase):
    """
    Test ItemBase class that represents a Patient

    """

    def __init__(self, id: str, **attributes):
        """
        Initializes PatientItem

        """
        super().__init__(id=id, **attributes)

    @property
    def id(self) -> str:
        """
        ID of the Patient

        """
        return self._attributes.get("id")


class PatientItemSet(ItemSet):
    """
    Test ItemSet class that represents a Patient

    """
    def __init__(self, items: List[PatientItem] = []):
        """
        Initializes PatientItemSet

        """
        super().__init__(items=items)

    @property
    def _item_class(self) -> Type[ItemBase]:
        """
        Instance type of items in this set.

        """
        return PatientItem


class TestItemBase(TestCase):
    """
    Unit tests for the common ItemBase class.

    """

    def test_eq(self):
        """
        Test __eq__

        """
        patient1 = PatientItem(id="patient_id_1")
        patient2 = PatientItem(id="patient_id_2")

        stream1 = StreamItem(id="stream_id_1")
        stream_with_patient1_id = StreamItem(id="patient_id_1")

        # Reflexive property
        self.assertEqual(patient1, patient1)

        # Same type different id
        self.assertNotEqual(patient1, patient2)

        # Different type and different id
        self.assertNotEqual(patient1, stream1)

        # Different type same id
        self.assertNotEqual(patient1, stream_with_patient1_id)

    def test_get(self):
        """
        Test __getattr__, __getitem__, and get

        """
        patient1 = PatientItem(id="patient_id", key1="val1")

        # __getitem__
        self.assertEqual("val1", patient1["key1"])

        # get
        self.assertEqual("val1", patient1.get("key1"))
        self.assertEqual(None, patient1.get("invalid_key"))
        self.assertEqual(0, patient1.get("invalid_key", 0))

    def test_repr(self):
        """
        Test __repr__

        """
        patient1 = PatientItem(id="patient_id")
        self.assertEqual(
            'PatientItem(\n\tid=patient_id,\n\tattributes='
            '{\'id\': \'patient_id\'}\n)',
            repr(patient1)
        )


        patient2 = PatientItem(id="patient_id", key1="val1")
        self.assertEqual(
            (
                "PatientItem(\n\tid=patient_id,\n\t"
                "attributes={'key1': 'val1', 'id': 'patient_id'}\n)"
            ),
            repr(patient2)
        )

    def test_to_dict(self):
        """
        Test to_dict

        """
        patient1 = PatientItem(id="patient_id")
        self.assertEqual({"id": "patient_id"}, patient1.to_dict())

        patient2 = PatientItem(
            id="patient_id",
            key1="val1",
            key2=2
        )
        self.assertEqual(
            {"id": "patient_id", "key1": "val1", "key2": 2},
            patient2.to_dict()
        )


class TestItemSet(TestCase):
    """
    Unit tests for the common ItemSet class.

    """

    test_patient_set = PatientItemSet(
        items=[
            PatientItem(id="patient1_id"),
            PatientItem(id="patient2_id", key1="val1"),
            PatientItem(id="patient3_id", key1=1, key2="val2"),
        ]
    )

    def test_iter(self):
        """
        Test __iter__

        """
        exp_patient_ids = ['patient1_id', 'patient2_id', 'patient3_id']
        for patient in self.test_patient_set:
            self.assertIn(patient.id, exp_patient_ids)
            exp_patient_ids.remove(patient.id)

        self.assertEqual([], exp_patient_ids)

    def test_len(self):
        """
        Test __len__

        """
        self.assertEqual(0, len(PatientItemSet()))
        self.assertEqual(3, len(self.test_patient_set))


    def test_get(self):
        """
        Test __getitem__ and get

        """
        # __getitem__
        self.assertEqual(
            PatientItem(id="patient1_id"),
            self.test_patient_set["patient1_id"]
        )

        # get
        self.assertEqual(
            PatientItem(id="patient2_id", key1="val1"),
            self.test_patient_set.get("patient2_id")
        )

    def test_add(self):
        """
        Test add

        """
        # Test successfully adding a new patient to a set
        patient_set = PatientItemSet()
        self.assertEqual(0, len(patient_set))

        new_patient = PatientItem(id="patient1_id")
        patient_set.add(new_patient)
        self.assertEqual(1, len(patient_set))
        self.assertEqual(new_patient, patient_set.get("patient1_id"))

        # Test adding multiple patients to a set
        patient_set = PatientItemSet()
        patient2 = PatientItem(id="patient2_id")
        patient_set.add(new_patient, new_patient, patient2)
        self.assertEqual(2, len(patient_set))
        self.assertEqual(new_patient, patient_set.get("patient1_id"))
        self.assertEqual(patient2, patient_set.get("patient2_id"))

        # Test raises TypeError when adding item with a different
        # type to the set.
        patient_set = PatientItemSet()
        new_stream = StreamItem(id="strean1_id")

        with self.assertRaisesRegex(
            TypeError,
            "cannot add"
        ):
            patient_set.add(new_stream)

    def test_remove(self):
        """
        Test remove

        """
        # Remove a patient by object or id
        patient1 = PatientItem(id="patient1_id")
        patient_set = PatientItemSet(
            items=[
                patient1,
                PatientItem(id="patient2_id", key1="val1"),
            ]
        )
        self.assertEqual(2, len(patient_set))

        patient_set.remove(patient1)
        self.assertEqual(1, len(patient_set))

        patient_set.remove("patient2_id")
        self.assertEqual(0, len(patient_set))

        # Remove multiple patients by object or id
        patient1 = PatientItem(id="patient1_id")
        patient_set = PatientItemSet(
            items=[
                patient1,
                PatientItem(id="patient2_id", key1="val1"),
            ]
        )
        self.assertEqual(2, len(patient_set))

        patient_set.remove(patient1, "patient2_id")
        self.assertEqual(0, len(patient_set))

    def test_ids(self):
        """
        Test ids

        """
        self.assertEqual(
            [],
            list(PatientItemSet().ids())
        )

        self.assertEqual(
            ["patient1_id", "patient2_id", "patient3_id"],
            list(self.test_patient_set.ids())
        )

    def test_str(self):
        """
        Test __str__

        """
        self.assertEqual(
            """PatientItemSet {
}""",
            str(PatientItemSet())
        )

        patient_set = PatientItemSet(
            items=[
                PatientItem(id="patient1_id"),
                PatientItem(id="patient2_id", key1="val1"),
                PatientItem(
                    id="patient3_id",
                    key1=1,
                    key2="val2"
                ),
                PatientItem(id="patient4_id"),
                PatientItem(id="patient5_id"),
            ]
        )

        self.assertEqual(
            (
                'PatientItemSet {\n'
                '	patient1_id\n'
                '	patient2_id\n'
                '	patient3_id\n'
                '	... (and 2 others)\n'
                '}'
            ),
            str(patient_set)
        )


    def test_to_list(self):
        """
        Test to_list

        """
        self.assertEqual([], PatientItemSet().to_list())
        self.assertEqual(
            [
                {'id': 'patient1_id'},
                {'id': 'patient2_id', 'key1': 'val1'},
                {'id': 'patient3_id', 'key1': 1, 'key2': 'val2'},
            ],
            self.test_patient_set.to_list()
        )

