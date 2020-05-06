"""
Error classes.

"""


class RuneError(Exception):
    """
    Base class for Rune SDK errors.

    """


class APIError(RuneError):
    """
    Rune API Error. Includes details about error type.

    """

    def __init__(self, status_code, details):
        """
        Init with HTTP status code and details
        """
        self.status_code = status_code
        self.details = details

        err_type = 'Error'
        if isinstance(details, dict) and 'type' in details:
            err_type = details['type']

        super().__init__(f'{status_code} {err_type}: {details}')
