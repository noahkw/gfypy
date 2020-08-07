import requests

from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.http.abstract_http import AbstractHttpClient


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class SyncHttpClient(AbstractHttpClient):
    def __init__(self):
        self._session = requests.Session()
        self._auth = None

    def request(self, route, **kwargs):
        no_auth = kwargs.pop('no_auth') if 'no_auth' in kwargs else False

        if self._auth is not None and not no_auth:
            resp = self._session.request(route.method, route.url, **kwargs, auth=self._auth)
        else:
            resp = self._session.request(route.method, route.url, **kwargs)

        content_type = resp.headers.get('content-type')

        if content_type == 'application/json':
            content = resp.json()
        else:
            content = resp.text

        if 200 <= resp.status_code < 300:
            return content
        elif resp.status_code in [401, 403]:
            if 'message' in content:
                raise GfypyAuthException(content['message'], resp.status_code, None)
            else:
                raise GfypyAuthException(content['errorMessage']['description'], resp.status_code,
                                         content['errorMessage']['code'])
        else:
            raise GfypyApiException(content['errorMessage'], resp.status_code)

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, token):
        self._auth = BearerAuth(token)
