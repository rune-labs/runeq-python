"""
Query data from the Rune Labs Stream API (V1).

"""
import csv
from logging import getLogger
from typing import Generator, Union
from urllib.parse import urljoin, urlencode

import requests

from runeq import config
from runeq.errors import APIError

try:
    import numpy as np
    USE_NUMPY = True
except ImportError:
    USE_NUMPY = False

log = getLogger(__name__)


def _str2float(s: str) -> Union[float, str]:
    """
    Convert string to a numeric type, if possible.

    """
    try:
        # if numpy is installed, use np.float64 instead of Python built-in
        if USE_NUMPY:
            return np.float64(s)
        else:
            return float(s)
    except ValueError:
        return s


def _check_response(r: requests.Response) -> None:
    """
    Raise an exception if the request was not successful.

    """
    if r.ok:
        return

    # When possible, the API returns details about what went wrong in
    # the json body of the response. Incorporate that detail into the error
    # raised.
    try:
        data = r.json()
    except Exception:
        r.raise_for_status()
        return

    if 'error' in data:
        raise APIError(r.status_code, data['error'])


class StreamV1Base:
    """
    Base class for requesting data from the Stream V1 API.

    """

    # Name of the resource (e.g. lfp, accel)
    _resource: str

    # Expression to use to query the availability timeseries for a resource.
    # Not supported for all resources.
    _availability = None

    def __init__(self, cfg: config.Config, **defaults):
        """
        Initialize with a Config and default query parameters.

        Args:
            config: Config, with settings used for all API requests
            **defaults: Default query parameters to use for all API requests.
                If a method accepts query parameters, they will be used to
                override these defaults for the related requests.

        :meta public:
        """
        self.config = cfg
        self.defaults = defaults

    def _update_params(self, params):
        """
        Update query params in place, using self.defaults.

        """
        for k in filter(lambda x: x not in params, self.defaults):
            params[k] = self.defaults[k]
        return params

    def get_json_response(self, **params) -> requests.Response:
        """
        Make a GET request to the resource's JSON endpoint.

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis, for this request.

        Returns:
            requests.Response

        """
        self._update_params(params)

        url = urljoin(
            self.config.stream_url,
            '/v1/{}.json'.format(self._resource)
        )
        log.debug(f'GET {url}?{urlencode(params)}')
        return requests.get(
            url,
            headers=self.config.auth_headers,
            params=params,
        )

    def iter_json_data(self, **params) -> Generator[dict, None, None]:
        """
        Iterate over JSON results, the resource’s JSON endpoint.

        Follows pagination to get a complete set of results, starting
        with the page specified in the `page` kwarg (or the first
        page, by default).

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis.

        Yields:
             dict with the "result" from the JSON body of each response.

        Raises:
            APIError: when a request fails
        """
        next_page = 1  # init with something truthy
        while next_page:
            r = self.get_json_response(**params)
            _check_response(r)
            data = r.json()

            next_page = data.get('next_page')
            params['page'] = next_page
            next_page_token = r.headers.get('X-Rune-Next-Page-Token')

            if next_page_token is not None:
                params['next_page_token'] = next_page_token
                params.pop('page', None)
            else:
                params.pop('next_page_token', None)

            yield data['result']

    @property
    def expr_availability(self):
        """
        Availability expression for this resource.

        Raises:
            NotImplementedError: if the resource doesn't support an
                availability query expression.

        """
        if not self._availability:
            raise NotImplementedError(f'{self.__class__.__name__} does not '
                                      f'support an availability query')

        return self._availability

    def iter_json_availability(self, **params) -> Generator[dict, None, None]:
        """
        Convenience method to query the JSON endpoint, using the availability
        expression. This may not be supported for all endpoints.

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis.

        Yields:
             dict with the "result" from the JSON body of each response.

        Raises:
            NotImplementedError: if the resource doesn't support an
                availability query expression.
        """
        params['expression'] = self.expr_availability
        yield from self.iter_json_data(**params)


class StreamV1CSVBase(StreamV1Base):
    """
    Base class for requesting data from the Stream V1 API, for resources that
    support both JSON and CSV data formats.

    """

    def get_csv_response(self, **params) -> requests.Response:
        """
        Make a GET request to the resource's CSV endpoint.

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis.

        Returns:
            requests.Response
        """
        self._update_params(params)

        url = urljoin(
            self.config.stream_url,
            '/v1/{}.csv'.format(self._resource)
        )

        log.debug(f'GET {url}?{urlencode(params)}')
        return requests.get(
            url,
            headers=self.config.auth_headers,
            params=params,
            stream=True,
        )

    def iter_csv_text(self, **params) -> Generator[str, None, None]:
        """
        Iterate over CSV text results, from the resource's CSV endpoint.

        Follows pagination to get a complete set of results, starting
        with the page specified in the `page` kwarg (or the first
        page, by default).

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis.

        Yields:
             text body of each response.

        Raises:
            APIError: when a request fails
        """

        # page will be maintained independently of the params value
        # to keep the page synchronized with the offset when the next
        # page token header field is present. This will allow the page
        # parameter to be added back to the params in the event that
        # the next page token header field is absent from the response.
        page = 0

        if 'page' in params:
            page = params['page']

        while True:
            r = self.get_csv_response(**params)
            _check_response(r)
            if not r.text:
                return

            yield r.text

            page += 1
            next_page_token = r.headers.get('X-Rune-Next-Page-Token')

            if next_page_token is not None:
                params['next_page_token'] = next_page_token
                params.pop('page', None)
            else:
                params['page'] = page
                params.pop('next_page_token', None)

    def iter_csv_availability(self, **params) -> Generator[dict, None, None]:
        """
        Convenience method to query the CSV endpoint, using the availability
        expression. May not be supported for all resources.

        Args:
            **params: Query parameters for the request. These override
                self.defaults, on a key-by-key basis.

        Yields:
             text body of each response.

        Raises:
            NotImplementedError: if the resource doesn't support an
                availability query expression.
        """
        params['expression'] = self.expr_availability
        yield from self.iter_csv_text(**params)

    def points(self, **params) -> Generator[dict, None, None]:
        """
        Iterate over points from CSV response, yielding dictionaries.

        This may involve multiple requests to the CSV endpoint, to follow
        pagination.

        Args:
            **params: query parameters for the request(s). These override
                self.defaults on a key-by-key basis.

        Yields:
             dict: Keys are the headers from the CSV response. Values are
             converted to numeric types where applicable. If numpy
             is available, np.float64 is used.

        """
        if USE_NUMPY:
            restval = np.NaN
        else:
            restval = None

        for body in self.iter_csv_text(**params):
            reader = csv.DictReader(body.splitlines(), restval=restval)
            for point in reader:
                for k in point:
                    if k is None:
                        # If a data row has more items than the header row,
                        # DictReader adds the overflow to a None key. This is
                        # unexpected behavior from the v1 API; log a warning,
                        # but return the data anyway (unconverted).
                        log.warning('Data row had too many values')
                    else:
                        if point[k] == '':
                            point[k] = restval
                        else:
                            point[k] = _str2float(point[k])

                yield point

    def __iter__(self) -> Generator[dict, None, None]:
        """
        Iterate over points from the CSV response, using self.points().

        Yields:
            dict for each line in the CSV response. Keys are the CSV headers.

        :meta public:
        """
        yield from self.points()


####################
# V1 API Resources #
####################


class Accel(StreamV1CSVBase):
    """
    Query accelerometry data streams.

    """
    _resource = 'accel'
    _availability = 'availability(accel)'


class Event(StreamV1Base):
    """
    Query patient events.

    """
    _resource = 'event'


class LFP(StreamV1CSVBase):
    """
    Query local field potential (LFP) data streams.

    """
    _resource = 'lfp'
    _availability = 'availability(lfp)'


class ProbabilitySymptom(StreamV1CSVBase):
    """
    Query the probability of a symptom.

    """
    _resource = 'probability_symptom'
    _availability = 'availability(probability)'


class Rotation(StreamV1CSVBase):
    """
    Query rotation data streams.

    """
    _resource = 'rotation'
    _availability = 'availability(rotation)'


class State(StreamV1CSVBase):
    """
    Query device state.

    """
    _resource = 'state'


####################
# V1Client Factory #
####################


class V1Client:
    """
    V1Client is a factory class. It holds configuration, which is used to
    initialize accessor classes for Stream V1 endpoints.

    """

    def __init__(self, cfg: config.Config):
        """
        Initialize client with a config.

        """
        self._cfg = cfg

    @property
    def config(self) -> config.Config:
        """
        Return configuration.

        """
        return self._cfg

    def Accel(self, **defaults) -> Accel:
        """
        Initialize an Accel accessor.

        Args:
            **defaults: Default query parameters

        """
        return Accel(self.config, **defaults)

    def Event(self, **defaults) -> Event:
        """
        Initialize an Event accessor.

        Args:
            **defaults: Default query parameters

        """
        return Event(self.config, **defaults)

    def LFP(self, **defaults) -> LFP:
        """
        Initialize an LFP accessor.

        Args:
            **defaults: Default query parameters

        """
        return LFP(self.config, **defaults)

    def ProbabilitySymptom(self, **defaults) -> ProbabilitySymptom:
        """
        Initialize a ProbabilitySymptom accessor.

        Args:
            **defaults: Default query parameters

        """
        return ProbabilitySymptom(self.config, **defaults)

    def Rotation(self, **defaults) -> Rotation:
        """
        Initialize a Rotation accessor.

        Args:
            **defaults: Default query parameters

        """
        return Rotation(self.config, **defaults)

    def State(self, **defaults) -> State:
        """
        Initialize a State accessor.

        Args:
            **defaults: Default query parameters

        """
        return State(self.config, **defaults)
