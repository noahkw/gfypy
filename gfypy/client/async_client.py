import asyncio
import json

from tqdm import tqdm

from gfypy.route import CustomRoute

from gfypy.client.abstract_client import AbstractGfypy
from gfypy.const import REDIRECT_URI, FILEDROP_ENDPOINT, GFYCAT_URL
from gfypy.exceptions import GfypyAuthException
from gfypy.http import AsyncHttpClient
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
