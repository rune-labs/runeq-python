"""
Query sleep data directly from the Strive API.

"""

from datetime import date, timedelta
from typing import Dict, List, Optional

from .client import StriveClient, global_strive_client


def get_sleep_metrics(
    patient_id: str,
    start_date: date,
    end_date: date,
    client: Optional[StriveClient] = None,
) -> List[Dict]:
    """Fetch sleep metrics for a patient.

    Data is fetched from the Strive API in segments of 30 days at a time.

    Args:
        patient_id: The patient ID.
        start_date: The start date for the query.
        end_date: The end date for the query.
        client: Optional StriveClient instance. If not provided, uses the global client.
    """

    client = client or global_strive_client()
    all_metrics = []
    # fetch sleep in chunks of 30 days
    chunk_size = timedelta(days=30)
    chunk_start = start_date
    while chunk_start <= end_date:
        # the end is either the end of the next 30 days or the end date if
        # earlier
        chunk_end = min(chunk_start + chunk_size, end_date)
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

        all_metrics.extend(resp.json()["data"]["sleep_metrics_healthkit"])
        chunk_start = chunk_end + timedelta(days=1)

    return all_metrics
