import json

import aiohttp

from gfypy.const import REDIRECT_URI
from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.http.abstract_http import AbstractHttpClient
from gfypy.route import Route


class BearerAuth(aiohttp.BasicAuth):
    def __init__(self, token):
        self.token = token

    def encode(self):
        return "Bearer " + self.token


class AsyncHttpClient(AbstractHttpClient):
    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        self._session = aiohttp.ClientSession()
        self._auth = None
        self.creds = {
            "access_token": None,
            "expires_in": None,
            "refresh_token": None,
            "refresh_token_expires_in": None,
            "resource_owner": None,
        }

    async def close(self):
        await self._session.close()

    async def request(self, route, **kwargs):
        no_auth = kwargs.pop("no_auth", False)
        refresh = kwargs.pop("refresh", True)

        async with self._session.request(
            route.method, route.url, **kwargs, auth=self._auth if not no_auth else None
        ) as resp:
            content_type = resp.headers.get("content-type")
            if content_type == "application/json":
                content = await resp.json()
            else:
                content = await resp.text()

            if 200 <= resp.status < 300:
                return content
            elif resp.status in [401, 403]:
                if refresh:
                    # try to refresh the oauth token in case it's become invalid
                    await self.refresh_oauth_token()

                    return await self.request(route, **kwargs, refresh=False)
                else:
                    if "message" in content:
                        raise GfypyAuthException(content["message"], resp.status, None)
                    else:
                        raise GfypyAuthException(
                            content["errorMessage"]["description"],
                            resp.status,
                            content["errorMessage"]["code"],
                        )
            else:
                raise GfypyApiException(
                    content["errorMessage"] if "message" in content else content,
                    resp.status,
                )

    async def get_oauth_token(self, code):
        payload = {
            "code": code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        }

        resp = await self.request(
            Route("POST", "/oauth/token"),
            data=json.dumps(payload),
            headers={"content-type": "application/json"},
        )

        self.creds = resp
        self.auth = resp["access_token"]

    async def refresh_oauth_token(self, **kwargs):
        payload = {
            "refresh_token": self.creds["refresh_token"],
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh",
        }

        resp = await self.request(
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
