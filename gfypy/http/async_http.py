import aiohttp

from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.http.abstract_http import AbstractHttpClient


class BearerAuth(aiohttp.BasicAuth):
    def __init__(self, token):
        self.token = token

    def encode(self):
        return "Bearer " + self.token


class AsyncHttpClient(AbstractHttpClient):
    def __init__(self):
        self._session = aiohttp.ClientSession()
        self._auth = None

    async def close(self):
        await self._session.close()

    async def request(self, route, **kwargs):
        no_auth = kwargs.pop('no_auth') if 'no_auth' in kwargs else False

        async with self._session.request(route.method, route.url, **kwargs, auth=self._auth) as resp:
            content_type = resp.headers.get('content-type')
            if content_type == 'application/json':
                content = await resp.json()
            else:
                content = await resp.text()

            if 200 <= resp.status < 300:
                return content
            elif resp.status in [401, 403]:
                if 'message' in content:
                    raise GfypyAuthException(content['message'], resp.status, None)
                else:
                    raise GfypyAuthException(content['errorMessage']['description'], resp.status,
                                             content['errorMessage']['code'])
            else:
                raise GfypyApiException(content['errorMessage'], resp.status)

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, token):
        self._auth = BearerAuth(token)
