import json
import time

from tqdm import tqdm

from gfypy.client.abstract_client import AbstractGfypy
from gfypy.const import GFYCAT_URL, FILEDROP_ENDPOINT, REDIRECT_URI
from gfypy.exceptions import GfypyAuthException, GfypyException
from gfypy.gfy import Gfy
from gfypy.http import SyncHttpClient
from gfypy.route import Route, CustomRoute
from gfypy.user import User


class Gfypy(AbstractGfypy):
    def __init__(self, client_id, client_secret, auth_file_path):
        super().__init__(client_id, client_secret, auth_file_path)
        self._http = SyncHttpClient()

    def authenticate(self):
        if not self._auth_file_path.is_file():
            print(f'Credentials file "{self._auth_file_path}" does not exist. Creating it now.')
            with open(self._auth_file_path, 'w') as auth_file:
                auth_file.write(json.dumps(self._auth))

        with open(self._auth_file_path, 'r') as auth_file:
            self._auth = json.loads(auth_file.read())

            try:
                self._refresh_oauth_token()
            except GfypyAuthException as e:
                if e.code == 'InvalidRefreshToken':
                    self._initial_auth()
                    self._auth_to_disk()
                else:
                    raise

    def _initial_auth(self):
        self._get_oauth_token(self._get_oauth_code())

    def _get_oauth_token(self, code):
        payload = {
            'code': code,
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }

        resp = self._http.request(Route('POST', '/oauth/token'), data=json.dumps(payload),
                                  headers={'content-type': 'application/json'})

        self._auth = resp
        self._http.auth = resp['access_token']

    def _refresh_oauth_token(self):
        payload = {
            'refresh_token': self._auth['refresh_token'],
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'refresh',
        }

        resp = self._http.request(Route('POST', '/oauth/token'), data=json.dumps(payload),
                                  headers={'content-type': 'application/json'})

        self._auth = resp
        self._http.auth = resp['access_token']

    def upload_from_file(self, filename, title='', tags=[], keep_audio=True, check_duplicate=False):
        key = self._get_key(title, tags, keep_audio, check_duplicate)
        payload = {
            'key': key
        }
        files = {
            'file': (key, open(filename, 'rb').read())
        }

        self._http.request(CustomRoute('POST', FILEDROP_ENDPOINT), data=payload, files=files, no_auth=True)
        status = self._check_upload_status(key)

        progress = tqdm(total=self.MAX_CHECKS)
        num_checks = 0
        while status['task'] != 'complete':
            if num_checks > self.MAX_CHECKS:
                # the gfycat was likely uploaded correctly, but gfycat is not sending 'task': 'complete'
                break
            status = self._check_upload_status(key)
            progress.update(1)
            num_checks += 1
            time.sleep(3)

        progress.close()
        gfy = self.get_gfycat(key)
        print(f'\n{filename} has been uploaded as {GFYCAT_URL}/{key}.')

        return gfy

    def get_followers(self, fetch_userdata=False):
        resp = self._http.request(Route('GET', '/me/followers'))

        if not fetch_userdata:
            return resp['followers']
        else:
            users = []
            for follower in resp['followers']:
                user = self.get_user(follower['follower_id'])
                user['follow_date'] = follower['follow_date']
                users.append(user)

            return users