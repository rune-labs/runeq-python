"""
Internal types and utilities. Not intended for external use.

"""

import time
from datetime import date, datetime
from typing import Union

_time_type = Union[int, float, date, datetime]


def _time_type_to_unix_secs(t: _time_type) -> Union[int, float]:
    """Standardize time input as timestamp (in unix secs)"""
    if isinstance(t, datetime):
        return t.timestamp()
    elif isinstance(t, date):
        return time.mktime(t.timetuple())
    else:
        return t
