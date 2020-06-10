from unittest import mock, TestCase
from typing import List, Dict

import numpy as np

from runeq import Config, stream, errors


def mock_get_json_response(
        bodies: List[dict],
        calls: List,
        status_code=200,
        headers: List[Dict[str, str]] = None
):
    """Return a function that can be used to mock .get_json_response()

    Args:
        bodies: list of JSON bodies to return from response.json()
        calls: list. Every time the function is called, args and kwargs will
            be appended to this list.
        status_code: status code to return for each response
        headers: the response header to apply
    """
    headers = headers or [{}] * len(bodies)

    num = 0

    def _func(*args, **kwargs):
        nonlocal num
        # add inputs to the list of calls that was provided
        calls.append((args, kwargs))

        resp = mock.MagicMock()
        resp.headers = headers[num]
        resp.status_code = status_code
        resp.ok = (status_code < 400)
        resp.json.return_value = bodies[num]
        num += 1
        return resp

    return _func


def mock_get_csv_response(
        bodies: List[str],
        calls: List,
        status_code=200,
        headers: List[Dict[str, str]] = None
):
    """Return a function that can be used to mock .get_csv_response()

    Args:
        bodies: list of response bodies to return from response.text
        calls: list. Every time the function is called, args and kwargs will
            be appended to this list.
        status_code: status code to return for each response
        headers: the response header to apply
    """
    headers = headers or [{}] * len(bodies)

    num = 0

    def _func(*args, **kwargs):
        nonlocal num
        # keep track of the kwargs that were used to call this
        calls.append((args, kwargs))

        resp = mock.MagicMock()
        resp.headers = headers[num]
        resp.status_code = status_code
        resp.ok = (status_code < 400)
        resp.text = bodies[num]
        num += 1
        return resp

    return _func


class TestStreamV1Client(TestCase):
    """
    Test stream.V1Client and the associated accessors.

    """

    def setUp(self) -> None:
        """
        Initialize a client, set up basic mocking.

        """
        self.cfg = Config(
            client_key_id='abc',
            client_access_key='abc123',
        )
        self.client = stream.V1Client(self.cfg)
        self.use_np_orig = stream.v1.USE_NUMPY
        stream.v1.USE_NUMPY = False

    def tearDown(self) -> None:
        """
        Tear down monkey-patching.

        """
        stream.v1.USE_NUMPY = self.use_np_orig

    @mock.patch('runeq.stream.v1.requests')
    def test_get_json_response(self, requests):
        """
        Test the signature of JSON requests.

        """
        for test_num, case in enumerate((
                (self.client.Accel, '/v1/accel.json'),
                (self.client.Event, '/v1/event.json'),
                (self.client.LFP, '/v1/lfp.json'),
                (
                        self.client.ProbabilitySymptom,
                        '/v1/probability_symptom.json'
                ),
                (self.client.Rotation, '/v1/rotation.json'),
                (self.client.State, '/v1/state.json'))
        ):
            resource_creator, endpoint = case
            resource = resource_creator(leslie='knope')
            resource.get_json_response(ron='swanson', test_num=test_num)
            requests.get.assert_has_calls([
                mock.call(
                    self.cfg.stream_url + endpoint,
                    headers=self.cfg.auth_headers,
                    params={
                        'leslie': 'knope',
                        'ron': 'swanson',
                        'test_num': test_num,
                    }
                ),
            ])

    @mock.patch('runeq.stream.v1.requests')
    def test_get_csv_response(self, requests):
        """
        Test the signature of CSV requests.

        """
        for test_num, case in enumerate((
                (self.client.Accel, '/v1/accel.csv'),
                (self.client.LFP, '/v1/lfp.csv'),
                (
                        self.client.ProbabilitySymptom,
                        '/v1/probability_symptom.csv'
                ),
                (self.client.Rotation, '/v1/rotation.csv'),
                (self.client.State, '/v1/state.csv'),
        )):
            resource_creator, endpoint = case
            resource = resource_creator(leslie='knope')
            resource.get_csv_response(ron='swanson', test_num=test_num)
            requests.get.assert_has_calls([
                mock.call(
                    self.cfg.stream_url + endpoint,
                    stream=True,
                    headers=self.cfg.auth_headers,
                    params={
                        'leslie': 'knope',
                        'ron': 'swanson',
                        'test_num': test_num,
                    }
                ),
            ])

    def test_iter_json_data_with_token(self):
        """
        Test the iterator over JSON responses, with new pagination.

        """
        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()

            mock_responses = [
                {'success': True, 'result': [], 'next_page': 1},
                {'success': True, 'result': []}
            ]

            calls = []
            resource.get_json_response = mock_get_json_response(
                mock_responses,
                calls,
                200,
                [
                    {'X-Rune-Next-Page-Token': 'MTIzNDU2MDAwMA=='},
                    {},
                ]
            )

            iterator = resource.iter_json_data(test_num=test_num)
            self.assertEqual(len(list(iterator)), 2)

            # Check that all parameters were kept the same across calls,
            # except for "page" (which must be incremented)
            self.assertEqual(calls, [
                ((), {'test_num': test_num}),
                (
                    (),
                    {
                        'test_num': test_num,
                        'next_page_token': 'MTIzNDU2MDAwMA=='
                    }
                )
            ])

    def test_iter_json_data(self):
        """
        Test the iterator over JSON responses, which follows pagination.

        """
        results = [
            {'a': 1},
            {'b': 2}
        ]
        mock_responses = [
            {'success': True, 'result': results[0], 'next_page': 1},
            {'success': True, 'result': results[1]}
        ]

        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.Event,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()

            #
            # Successful Requests
            #
            calls = []
            resource.get_json_response = mock_get_json_response(
                mock_responses,
                calls
            )

            # Check the results
            num_results = 0
            iterator = resource.iter_json_data(test_num=test_num)
            for i, actual in enumerate(iterator):
                self.assertEqual(results[i], actual)
                num_results += 1

            self.assertEqual(num_results, 2)

            # Check that all parameters were kept the same across calls,
            # except for "page" (which must be incremented)
            self.assertEqual(calls, [
                ((), {'test_num': test_num}),
                ((), {'test_num': test_num, 'page': 1})
            ])

            #
            # Request Error
            # Iterator should check the response status for each request
            #
            err_details = {
                "message": "i am an intentional error!",
                "type": "TestError",
            }
            resource.get_json_response = mock_get_json_response(
                [{'success': False, 'error': err_details}],
                [],
                status_code=404,
            )

            with self.assertRaises(errors.APIError) as e:
                next(resource.iter_json_data())

            err = e.exception
            self.assertEqual(err.status_code, 404)
            self.assertEqual(err.details, err_details)

    def test_iter_csv_data_with_token(self):
        """
        Test the iterator over CSV responses, which follows new pagination

        """
        mock_responses = [
            'good,better\nskiing,hiking\n',
            'good,better\ncupcakes,brownies\n',
            '',
        ]

        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()

            #
            # Successful Requests
            #
            calls = []
            resource.get_csv_response = mock_get_csv_response(
                mock_responses,
                calls,
                200,
                [
                    {'X-Rune-Next-Page-Token': 'MTIzNDU2MDAwMA=='},
                    {'X-Rune-Next-Page-Token': 'MTIzNDU2MDAwMA=='},
                    {},
                ],
            )

            # Check the results
            iterator = resource.iter_csv_text(test_num=test_num)
            self.assertEqual(len(list(iterator)), 2)

            # Check that all parameters were kept the same across calls,
            # except for "next_page_token" (which will normally be different
            # for each response)
            self.assertEqual(calls, [
                ((), {'test_num': test_num}),
                (
                    (),
                    {
                        'test_num': test_num,
                        'next_page_token': 'MTIzNDU2MDAwMA=='
                    }
                ),
                (
                    (),
                    {
                        'test_num': test_num,
                        'next_page_token': 'MTIzNDU2MDAwMA=='
                    }
                ),
            ])

    def test_iter_csv_data(self):
        """
        Test the iterator over CSV responses, which follows pagination
        """
        mock_responses = [
            'good,better\nskiing,hiking\n',
            'good,better\ncupcakes,brownies\n',
            '',
        ]

        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()

            #
            # Successful Requests
            #
            calls = []
            resource.get_csv_response = mock_get_csv_response(
                mock_responses,
                calls,
            )

            # Check the results
            num_results = 0
            iterator = resource.iter_csv_text(test_num=test_num)
            for i, actual in enumerate(iterator):
                self.assertEqual(mock_responses[i], actual)
                num_results += 1

            # although there are 3 responses, the last (empty) body should not
            # be returned by the iterator
            self.assertEqual(num_results, 2)

            # Check that all parameters were kept the same across calls,
            # except for "page" (which must be incremented)
            self.assertEqual(calls, [
                ((), {'test_num': test_num}),
                ((), {'test_num': test_num, 'page': 1}),
                ((), {'test_num': test_num, 'page': 2}),
            ])

            #
            # Request Error
            # Iterator should check the response status for each request
            #
            err_details = {
                "message": "i am an intentional error!",
                "type": "TestError",
            }
            # note: CSV endpoints return JSON on API errors
            resource.get_csv_response = mock_get_json_response(
                [{'success': False, 'error': err_details}],
                [],
                status_code=404,
            )

            with self.assertRaises(errors.APIError) as e:
                next(resource.iter_csv_text())

            err = e.exception
            self.assertEqual(err.status_code, 404)
            self.assertEqual(err.details, err_details)

    def test_iter_points(self):
        """
        Test iterating over data as points.
        """
        mock_responses = [
            'lower,higher,label\n1,2,ints\n3.5,6.7,floats\n',
            'lower,higher,label\n,8.9,missing data\n',
            '',
        ]
        expected = [
            {'lower': 1, 'higher': 2, 'label': 'ints'},
            {'lower': 3.5, 'higher': 6.7, 'label': 'floats'},
            {'lower': None, 'higher': 8.9, 'label': 'missing data'},
        ]

        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()
            # replace get_csv_response on the resource
            resource.get_csv_response = mock_get_csv_response(
                mock_responses,
                [],
            )

            for i, point in enumerate(resource.points()):
                self.assertDictEqual(expected[i], point)

            # replace get_csv_response again, to restart the mock responses
            resource.get_csv_response = mock_get_csv_response(
                mock_responses,
                [],
            )

            for i, point in enumerate(resource):
                self.assertDictEqual(expected[i], point)
                # check dtype for "higher", which always has a numeric
                # value in the test data
                self.assertNotIsInstance(point['higher'], np.float64)

    def test_iter_points_numpy(self):
        """
        Test iterating over data as points, using Numpy to convert.

        """
        stream.v1.USE_NUMPY = True

        mock_responses = [
            'lower,higher,label\n1,2,ints\n3.5,6.7,floats\n',
            'lower,higher,label\n,8.9,missing data\n',
            '',
        ]
        expected = [
            {'lower': 1, 'higher': 2, 'label': 'ints'},
            {'lower': 3.5, 'higher': 6.7, 'label': 'floats'},
            {'lower': np.NaN, 'higher': 8.9, 'label': 'missing data'},
        ]

        for test_num, resource_creator in enumerate((
                self.client.Accel,
                self.client.LFP,
                self.client.ProbabilitySymptom,
                self.client.Rotation,
                self.client.State,
        )):
            resource = resource_creator()
            # replace get_csv_response on the resource
            resource.get_csv_response = mock_get_csv_response(
                mock_responses,
                [],
            )

            for i, point in enumerate(resource.points()):
                self.assertDictEqual(expected[i], point)
                # check dtype for "higher", which always has a numeric
                # value in the test data
                self.assertIsInstance(point['higher'], np.float64)
