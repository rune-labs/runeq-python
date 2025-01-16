"""
Tests for fetching strive data.

"""

from datetime import date
from unittest import TestCase, mock

from runeq.config import Config
from runeq.resources.client import StriveClient
from runeq.resources.sleep import get_sleep_metrics


class TestStriveData(TestCase):
    """
    Unit tests for the data queries in the strive module.

    """

    def setUp(self):
        """
        Set up mock graph client for testing.

        """
        self.strive_client = StriveClient(
            Config(client_key_id="test", client_access_key="config")
        )
        self.maxDiff = None

    @mock.patch("runeq.resources.client.requests.get")
    def test_get_sleep_metrics(self, mock_requests):
        """
        Test get sleep metrics for a given patient.

        """
        expected_data_dec = {
            "data": {
                "sleep_metrics_healthkit": [
                    {
                        "date": "2024-12-01",
                        "id": 1,
                        "qa_large_gaps": False,
                        "qa_stage_overlap": False,
                        "sleep_start_time": 1733108400.0,  # 2024-12-01 22:00:00
                        "sleep_end_time": 1733140800.0,  # 2024-12-02 07:00:00
                        "timezone": "America/New_York",
                        "total_sleep_time": 500,
                        "total_stage_time_core": 125,
                        "total_stage_time_deep": 250,
                        "total_stage_time_rem": 125,
                        "total_stage_time_unspecified": 125,
                        "waso": 25,
                        "number_of_awakenings": 2,
                    }
                ]
            }
        }
        expected_data_jan = {
            "data": {
                "sleep_metrics_healthkit": [
                    {
                        "date": "2025-01-09",
                        "id": 1,
                        "qa_large_gaps": False,
                        "qa_stage_overlap": False,
                        "sleep_start_time": 1736391600.0,  # 2025-01-08 22:00:00
                        "sleep_end_time": 1736427600.0,  # 2025-01-09 08:00:00
                        "timezone": "America/New_York",
                        "total_sleep_time": 500,
                        "total_stage_time_core": 125,
                        "total_stage_time_deep": 250,
                        "total_stage_time_rem": 125,
                        "total_stage_time_unspecified": 125,
                        "waso": 25,
                        "number_of_awakenings": 2,
                    }
                ]
            }
        }

        expected_metrics = [
            {
                "date": "2024-12-01",
                "id": 1,
                "qa_large_gaps": False,
                "qa_stage_overlap": False,
                "sleep_start_time": 1733108400.0,
                "sleep_end_time": 1733140800.0,
                "timezone": "America/New_York",
                "total_sleep_time": 500,
                "total_stage_time_core": 125,
                "total_stage_time_deep": 250,
                "total_stage_time_rem": 125,
                "total_stage_time_unspecified": 125,
                "waso": 25,
                "number_of_awakenings": 2,
            },
            {
                "date": "2025-01-09",
                "id": 1,
                "qa_large_gaps": False,
                "qa_stage_overlap": False,
                "sleep_start_time": 1736391600.0,
                "sleep_end_time": 1736427600.0,
                "timezone": "America/New_York",
                "total_sleep_time": 500,
                "total_stage_time_core": 125,
                "total_stage_time_deep": 250,
                "total_stage_time_rem": 125,
                "total_stage_time_unspecified": 125,
                "waso": 25,
                "number_of_awakenings": 2,
            },
        ]

        # Mock a paginated response
        mock_response1 = mock.Mock()
        mock_response1.ok = True
        mock_response1.json.return_value = expected_data_dec

        mock_response2 = mock.Mock()
        mock_response2.ok = True
        mock_response2.json.return_value = expected_data_jan

        mock_requests.side_effect = [mock_response1, mock_response2]
        actual = get_sleep_metrics(
            "test_patient_id",
            start_date=date(2024, 12, 1),
            end_date=date(2025, 1, 10),
            client=self.strive_client,
        )
        expected = expected_metrics
        self.assertEqual(expected, actual)
        self.assertEqual(mock_requests.call_count, 2)
