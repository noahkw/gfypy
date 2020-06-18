from urllib.parse import quote

import requests

from .exceptions import GfypyAuthException, GfypyApiException


class Route:
    BASE = 'https://api.gfycat.com/v1'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        url = self.BASE + self.path
        if parameters:
            self.url = url.format(**{k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        else:
            self.url = url


class CustomRoute:
    def __init__(self, method, base, path=None):
        self.method = method
        self.base = base
        self.path = path
        if path is not None:
            self.url = self.base + self.path
        else:
            self.url = self.base


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class HttpClient:
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
