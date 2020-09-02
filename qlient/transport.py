from typing import Dict, Union

import requests
from promise import Promise
from requests import Session, Response

from qlient.settings import Settings
from qlient.utils import get_version


class Transporter:
    """
    A transport object handles communication between client and server.

    Optionally a custom session can be passed by and an operation timeout be set.
    """

    def __init__(self, session=None, operation_timeout=None):
        """
        Create a new Transporter object.

        :param session: (optional) a requests session object
        :param operation_timeout: (optional) requests operation timeout
        """
        self.operation_timeout = operation_timeout
        self.session: Session = session or requests.sessions.session()
        self.session.headers["User-Agent"] = f"Graphy/{get_version()} (https://pypi.org/project/python-graphy/)"

    def post(
            self,
            endpoint: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Union[Response, Dict]:
        """
        Wrapper for the requests.post() method.

        :param endpoint: holds the request endpoint
        :param query: holds the query string
        :param variables: holds the query variables if there are any
        :param operation_name: holds the operation name. Used for reading response data
        :param settings: holds the clients settings
        :return:
        """
        response = self.session.post(
            endpoint,
            json={
                "query": query,
                "variables": variables
            },
            timeout=self.operation_timeout
        )

        if settings.return_requests_response:
            return response
        else:
            response_json: Dict = response.json()
            try:
                return response_json[settings.default_response_key][operation_name]
            except KeyError:
                raise KeyError("Key not found in response. Try to set Settings(return_requests_response=True)")


class PromiseTransporter(Transporter):
    """
    A promise transporter returns Promises instead of the Response.
    Use this when you do not want to wait for the request to finish and continue to run with your code.
    """

    def post(
            self,
            endpoint: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Promise[Union[Response, Dict]]:
        """
        This method wraps the parents post method in a Promise.
        """
        return Promise(
            lambda resolve, reject: resolve(super(PromiseTransporter, self).post(
                endpoint, query, variables, operation_name, settings
            ))
        )


class AsyncTransporter(Transporter):
    """
    An async transporter wraps the default post in an async method.
    Use this for async programming.
    """

    async def post(
            self,
            endpoint: str,
            query: str,
            variables: Dict,
            operation_name: str,
            settings: Settings
    ) -> Union[Response, Dict]:
        """
        This method wraps the parents post method in an awaitable.
        """
        return super().post(endpoint, query, variables, operation_name, settings)
