import asyncio
import json

from gfypy.client.abstract_client import AbstractGfypy
from gfypy.const import REDIRECT_URI, FILEDROP_ENDPOINT, GFYCAT_URL
from gfypy.exceptions import GfypyAuthException
from gfypy.gfy import Gfy
from gfypy.http import AsyncHttpClient
from gfypy.route import CustomRoute
from gfypy.route import Route


class AsyncGfypy(AbstractGfypy):
    def __init__(self, client_id, client_secret, auth_file_path):
        super().__init__(client_id, client_secret, auth_file_path)
        self._http = AsyncHttpClient()

    async def authenticate(self):
        if not self._auth_file_path.is_file():
            print(f'Credentials file "{self._auth_file_path}" does not exist. Creating it now.')
            with open(self._auth_file_path, 'w') as auth_file:
                auth_file.write(json.dumps(self._auth))

        with open(self._auth_file_path, 'r') as auth_file:
            self._auth = json.loads(auth_file.read())

            try:
                await self._refresh_oauth_token()
            except GfypyAuthException as e:
                if e.code == 'InvalidRefreshToken':
                    await self._initial_auth()
                    self._auth_to_disk()
                else:
                    raise

    async def close(self):
        await self._http.close()

    async def _initial_auth(self):
        await self._get_oauth_token(self._get_oauth_code())

    async def _get_oauth_token(self, code):
        payload = {
            'code': code,
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }

        resp = await self._http.request(Route('POST', '/oauth/token'), data=json.dumps(payload),
                                        headers={'content-type': 'application/json'})

        self._auth = resp
        self._http.auth = resp['access_token']

    async def _refresh_oauth_token(self):
        payload = {
            'refresh_token': self._auth['refresh_token'],
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'refresh',
        }

        resp = await self._http.request(Route('POST', '/oauth/token'), data=json.dumps(payload),
                                        headers={'content-type': 'application/json'})

        self._auth = resp
        self._http.auth = resp['access_token']

    async def upload_from_file(self, filename, title='', tags=[], keep_audio=True, check_duplicate=False):
        key = await self._get_key(title, tags, keep_audio, check_duplicate)
        payload = {
            'key': key
        }
        files = {
            'file': (key, open(filename, 'rb').read())
        }

        await self._http.request(CustomRoute('POST', FILEDROP_ENDPOINT), data=payload, files=files, no_auth=True)
        status = await self._check_upload_status(key)

        num_checks = 0
        while status['task'] != 'complete':
            if num_checks > self.MAX_CHECKS:
                # the gfycat was likely uploaded correctly, but gfycat is not sending 'task': 'complete'
                break
            status = await self._check_upload_status(key)
            num_checks += 1
            await asyncio.sleep(3)

        gfy = await self.get_gfycat(key)
        print(f'\n{filename} has been uploaded as {GFYCAT_URL}/{key}.')

        return gfy

    async def user_feed_generator(self, user_id=None, per_request=100):
        if not 20 <= per_request <= 100:
            print(f'Number per request needs to be between 20 and 100.')
            return

        i = 0
        cursor = ''

        if user_id is None:
            route = Route('GET', '/me/gfycats')
        else:
            route = Route('GET', '/users/{id}/gfycats', id=user_id)

        while True:
            resp = await self._http.request(route, params={'count': per_request, 'cursor': cursor})

            cursor = resp['cursor']
            new_gfys = Gfy.from_dict_list(self, resp['gfycats'])
            yield new_gfys

            if len(new_gfys) < per_request:
                print('Got no new entries from Gfycat. Stopping here.')
                break

    async def get_user_feed(self, user_id=None, limit=100, sort_by=None, desc=True, filter_predicate=None):
        if limit % 100 != 0 and limit >= 0:
            print(f'Limit needs to be divisible by 100. Rounding up.')

        gfycats = []

        async for gfy_sublist in self.user_feed_generator(user_id=user_id, per_request=100):
            gfycats.extend(gfy_sublist)

            if len(gfycats) >= limit >= 0:
                break

        if filter_predicate:
            gfycats = [g for g in gfycats if filter_predicate(g)]

        if sort_by:
            gfycats = sorted(gfycats, key=lambda gfy: getattr(gfy, sort_by), reverse=desc)

        return gfycats
