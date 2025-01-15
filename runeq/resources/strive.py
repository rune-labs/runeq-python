"""
Query data directly from the Strive API.

"""

from rich import print

from .client import global_strive_client, StriveClient
from datetime import date, timedelta
from typing import List, Dict, Optional


def get_sleep_metrics(
    patient_id: str, start_date: date, end_date: date, client: Optional[StriveClient]
) -> List[Dict]:
    """Fetch sleep metrics for a patient.

    Args:
        patient_id: The patient ID.
        start_date: The start date for the query.
        end_date: The end date for the query."""

    client = client or global_strive_client()
    all_metrics = []
    chunk_size = timedelta(days=30)
    chunk_start = start_date
    print(chunk_start, end_date)
    while chunk_start <= end_date:
        chunk_end = min(chunk_start + chunk_size, end_date)
        print(chunk_start, chunk_end)
        resp = client.get(
            "/api/v3/sleep_metrics",
            params={
                "patient_id": patient_id,
                "start_date": chunk_start.strftime("%Y-%m-%d"),
                "end_date": chunk_end.strftime("%Y-%m-%d"),
            },
        )
        # if non-200, raise exception
        resp.raise_for_status()

        print("resp", resp.json())
        all_metrics.extend(resp.json()["data"]["sleep_metrics_healthkit"])
        chunk_start = chunk_end + timedelta(days=1)

    return all_metrics
