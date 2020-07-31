import aiohttp
from tqdm import tqdm

from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.gfy import Gfy
from gfypy.http.abstract_http import AbstractHttpClient
from gfypy.route import Route


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

    async def get_user_feed(self, user_id=None, limit=20, sort_by=None, desc=True, filter_predicate=None):
        if limit % 100 != 0:
            print(f'Limit needs to be divisible by 100. Rounding up.')

        gfycats = []
        i = 0
        cursor = ''

        if user_id is None:
            route = Route('GET', '/me/gfycats')
        else:
            route = Route('GET', '/users/{id}/gfycats', id=user_id)

        progress = tqdm(total=limit)

        while i < limit or limit < 0:
            resp = await self.request(route, params={'count': 100, 'cursor': cursor})

            cursor = resp['cursor']
            new_gfys = Gfy.from_dict_list(self, resp['gfycats'])
            gfycats.extend(new_gfys)
            progress.update(len(new_gfys))

            if i == len(gfycats):
                print('Got no new entries from Gfycat. Stopping here.')
                break
            i = len(gfycats)

        progress.close()

        if filter_predicate:
            gfycats = [g for g in gfycats if filter_predicate(g)]

        if sort_by:
            gfycats = sorted(gfycats, key=lambda k: k[sort_by], reverse=desc)

        return gfycats
