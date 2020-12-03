import json

import requests

from gfypy.const import REDIRECT_URI
from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.http.abstract_http import AbstractHttpClient
from gfypy.route import Route


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class SyncHttpClient(AbstractHttpClient):
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = requests.Session()
        self._auth = None
        self.creds = {
            "access_token": None,
            "expires_in": None,
            "refresh_token": None,
            "refresh_token_expires_in": None,
            "resource_owner": None,
        }

    def close(self):
        self._session.close()

    def request(self, route, **kwargs):
        no_auth = kwargs.pop("no_auth", False)
        refresh = kwargs.pop("refresh", True)

        if self._auth is not None and not no_auth:
            resp = self._session.request(
                route.method, route.url, **kwargs, auth=self._auth
            )
        else:
            resp = self._session.request(route.method, route.url, **kwargs)

        content_type = resp.headers.get("content-type")

        if content_type == "application/json":
            content = resp.json()
        else:
            content = resp.text

        if 200 <= resp.status_code < 300:
            return content
        elif resp.status_code in [401, 403]:
            if refresh:
                # try to refresh the oauth token in case it's become invalid
                self.refresh_oauth_token()

                return self.request(route, **kwargs, refresh=False)
            else:
                if "message" in content:
                    raise GfypyAuthException(content["message"], resp.status_code, None)
                else:
                    raise GfypyAuthException(
                        content["errorMessage"]["description"],
                        resp.status_code,
                        content["errorMessage"]["code"],
                    )
        else:
            raise GfypyApiException(
                content["errorMessage"] if "message" in content else content,
                resp.status_code,
            )

    def get_oauth_token(self, code):
        payload = {
            "code": code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        }

        resp = self.request(
            Route("POST", "/oauth/token"),
            data=json.dumps(payload),
            headers={"content-type": "application/json"},
        )

        self.creds = resp
        self.auth = resp["access_token"]

    def refresh_oauth_token(self, **kwargs):
        payload = {
            "refresh_token": self.creds["refresh_token"],
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh",
        }

        resp = self.request(
            Route("POST", "/oauth/token"),
            data=json.dumps(payload),
            headers={"content-type": "application/json"},
            **kwargs
        )

        self.creds = resp
        self.auth = resp["access_token"]

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, token):
        self._auth = BearerAuth(token)
