"""
Tests for the v2 common library.

"""
from textwrap import dedent
from unittest import TestCase

from runeq.v2sdk.common import SetMemberBase


class TestSetMemberBase(TestCase):
    """
    Tests for the resource collection member class.

    """

    maxDiff = None


    def test_nested_model(self):
        """
        Test modeling a nested structure with relations.

        """
        class Bar(SetMemberBase):
            pass

        class Baz(SetMemberBase):
            pass

        class Foo(SetMemberBase):
            _relations = {
                'bar': Bar,
                'baz': Baz
            }

        foo = Foo({
            'id': 'foo-llama',
            'fieldOne': 'value1',
            'bar': {
                'id': 'bar-llamabar,bar',
                'fieldTwo': 'value2'
            },
            'baz': [
                {
                    'fieldThree': 'value3'
                },
                {
                    'fieldThree': 'value4'
                }
            ]
        })

        self.assertEqual('foo', foo.resource)
        self.assertEqual('llama', foo.id)
        self.assertEqual('value1', foo.field_one)
        self.assertEqual('value1', foo['fieldOne'])
        self.assertEqual('llamabar', foo.bar.id)
        self.assertEqual('value2', foo.bar.field_two)
        self.assertEqual('value3', foo.baz[0].field_three)
        self.assertEqual('value4', foo.baz[1].field_three)

        self.assertEqual(
            dedent(
                '''
                foo {
                    id: llama
                    field_one: value1
                    bar: bar {
                        id: llamabar
                        field_two: value2
                    }
                    baz: [
                        baz {
                            field_three: value3
                        }
                        baz {
                            field_three: value4
                        }
                    ]
                }
                '''
            ).strip(),
            str(foo)
        )
