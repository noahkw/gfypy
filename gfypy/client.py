import json
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

import requests

from gfypy.exceptions import GfypyApiException, GfypyAuthException
from gfypy.models import Gfy, User


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class AuthCallbackRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<h2>You may close this window now!</h2>", 'UTF-8'))
        query = urlparse(self.path).query
        query_components = dict(qc.split('=') for qc in query.split('&'))
        code = query_components['code']
        self.server.code = code


class Gfypy:
    GFYCAT_URL = 'https://gfycat.com'
    AUTH_ENDPOINT = 'https://gfycat.com/oauth/authorize'
    ACCESS_TOKEN_ENDPOINT = 'https://api.gfycat.com/v1/oauth/token'
    REDIRECT_URI = 'http://localhost:8000/callback'
    GFYCATS_ENDPOINT = 'https://api.gfycat.com/v1/gfycats'
    FILEDROP_ENDPOINT = 'https://filedrop.gfycat.com/'
    USERS_ENDPOINT = 'https://api.gfycat.com/v1/users'
    ME_ENDPOINT = 'https://api.gfycat.com/v1/me'
    UPLOAD_STATUS_ENDPOINT = 'https://api.gfycat.com/v1/gfycats/fetch/status'
    USERS_ENDPOINT = 'https://api.gfycat.com/v1/users'

    def __init__(self, client_id, client_secret, auth_file_path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_file_path = Path(auth_file_path)
        self.bearer_auth = None
        self.auth = {
            'access_token': None,
            'expires_in': None,
            'refresh_token': None,
            'refresh_token_expires_in': None,
            'resource_owner': None
        }
        self.session = requests.Session()

    def authenticate(self):
        if not self.auth_file_path.is_file():
            print(f'Credentials file "{self.auth_file_path}" does not exist. Creating it now.')
            with open(self.auth_file_path, 'w') as auth_file:
                auth_file.write(json.dumps(self.auth))

        with open(self.auth_file_path, 'r') as auth_file:
            self.auth = json.loads(auth_file.read())
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

    def _get_oauth_code(self):
        """
        Gets authorization token
        """
        server = ThreadingHTTPServer(('localhost', 8000), AuthCallbackRequestHandler)
        server.code = None
        server_thread = Thread(target=server.serve_forever)
        server_thread.daemon = False
        server_thread.start()

        auth_url = f'{Gfypy.AUTH_ENDPOINT}?client_id={self.client_id}' \
                   f'&scope=all' \
                   f'&state=Gfypy' \
                   f'&response_type=code' \
                   f'&redirect_uri={Gfypy.REDIRECT_URI}'
        webbrowser.open(auth_url)

        while server.code is None:
            time.sleep(1)

        assassin = Thread(target=server.shutdown)
        assassin.daemon = True
        assassin.start()

        return server.code

    def _get_oauth_token(self, code):
        payload = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': Gfypy.REDIRECT_URI
        }

        resp = self.session.post(Gfypy.ACCESS_TOKEN_ENDPOINT, data=json.dumps(payload),
                                 headers={'content-type': 'application/json'})

        if resp.status_code != 200:
            raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                     resp.json()['errorMessage']['code'])

        self.auth = resp.json()
        self.bearer_auth = BearerAuth(resp.json()['access_token'])

    def _refresh_oauth_token(self):
        payload = {
            'refresh_token': self.auth['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh',
        }

        resp = self.session.post(Gfypy.ACCESS_TOKEN_ENDPOINT, data=json.dumps(payload),
                                 headers={'content-type': 'application/json'})

        if resp.status_code != 200:
            raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                     resp.json()['errorMessage']['code'])

        self.auth = resp.json()
        self.bearer_auth = BearerAuth(resp.json()['access_token'])

    def _auth_to_disk(self):
        with open(self.auth_file_path, 'w') as auth_file:
            auth_file.write(json.dumps(self.auth))

    def _get_key(self, title='', tags=[], keep_audio=True, check_duplicate=False):
        payload = {
            'title': title,
            'tags': tags,
            'keepAudio': keep_audio,
            'noMd5': not check_duplicate
        }

        resp = self.session.post(Gfypy.GFYCATS_ENDPOINT, data=json.dumps(payload),
                                 auth=self.bearer_auth, headers={'content-type': 'application/json'})

        if resp.status_code != 200:
            raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

        return resp.json()['gfyname']

    def upload_from_file(self, filename, title='', tags=[], keep_audio=True, check_duplicate=False):
        """
        Upload a local file to gfycat
        :param title:
        :param tags:
        :param filename:
        :param keep_audio:
        :param check_duplicate:
        :return:
        """
        key = self._get_key(title, tags, keep_audio, check_duplicate)
        payload = {
            'key': key
        }
        files = {
            'file': (key, open(filename, 'rb').read())
        }

        resp = self.session.post(Gfypy.FILEDROP_ENDPOINT, data=payload, files=files)

        if resp.status_code != 204:
            raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

        status = self._check_upload_status(key)

        while status['task'] != 'complete':
            time.sleep(3)
            status = self._check_upload_status(key)
            print(status)

        print(f'{filename} has been uploaded as {Gfypy.GFYCAT_URL}/{key}.')

        gfy = self.get_gfycat(key)
        return gfy

    def _check_upload_status(self, gfy_key):
        resp = self.session.get(f'{Gfypy.UPLOAD_STATUS_ENDPOINT}/{gfy_key}', auth=self.bearer_auth)

        if resp.status_code != 200:
            raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

        return resp.json()

    def get_user_feed(self, user_id, limit=20, sort_by=None, desc=True, filter_predicate=None):
        if limit % 10 != 0:
            print(f'Limit needs to be divisible by 10. Rounding up.')

        request_url = f'{Gfypy.USERS_ENDPOINT}/{user_id}/gfycats'
        gfycats = []

        i = 0
        cursor = ''
        while i < limit:
            resp = self.session.get(f'{request_url}?count=100&cursor={cursor}', auth=self.bearer_auth)

            if resp.status_code != 200:
                if resp.status_code == 401:
                    raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                             resp.json()['errorMessage']['code'])
                else:
                    raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

            cursor = resp.json()['cursor']
            gfycats.extend(Gfy.from_dict_list(self, resp.json()['gfycats']))
            if i == len(gfycats):
                print('Got no new entries from Gfycat. Stopping here.')
                break
            i = len(gfycats)
            print(i)

        if filter_predicate:
            gfycats = [g for g in gfycats if filter_predicate(g)]

        if sort_by:
            gfycats = sorted(gfycats, key=lambda k: k[sort_by], reverse=desc)

        return gfycats

    def get_own_feed(self, limit=20, sort_by=None, desc=True, filter_predicate=None):
        if limit % 10 != 0:
            print(f'Limit needs to be divisible by 10. Rounding up.')

        request_url = f'{Gfypy.ME_ENDPOINT}/gfycats'
        gfycats = []

        i = 0
        cursor = ''
        while i < limit:
            resp = self.session.get(f'{request_url}?count=100&cursor={cursor}', auth=self.bearer_auth)

            if resp.status_code != 200:
                if resp.status_code == 401:
                    raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                             resp.json()['errorMessage']['code'])
                else:
                    raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

            cursor = resp.json()['cursor']
            gfycats.extend(Gfy.from_dict_list(self, resp.json()['gfycats']))
            if i == len(gfycats):
                print('Got no new entries from Gfycat. Stopping here.')
                break
            i = len(gfycats)
            print(i)

        if filter_predicate:
            gfycats = [g for g in gfycats if filter_predicate(g)]

        if sort_by:
            gfycats = sorted(gfycats, key=lambda k: k[sort_by], reverse=desc)

        return gfycats

    def get_gfycat(self, _id):
        resp = self.session.get(f'{Gfypy.GFYCATS_ENDPOINT}/{_id}', auth=self.bearer_auth)

        if resp.status_code != 200:
            raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

        return Gfy.from_dict(self, resp.json()['gfyItem'])

    def _set_gfycat_title(self, _id, new_title):
        payload = {
            'value': new_title
        }

        resp = self.session.put(f'{Gfypy.ME_ENDPOINT}/gfycats/{_id}/title', auth=self.bearer_auth,
                                data=json.dumps(payload))

        if resp.status_code != 204:
            if resp.status_code == 401:
                raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                         resp.json()['errorMessage']['code'])
            else:
                raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

    def _delete_gfycat_title(self, _id):
        resp = self.session.delete(f'{Gfypy.ME_ENDPOINT}/gfycats/{_id}/title', auth=self.bearer_auth)

        if resp.status_code != 204:
            if resp.status_code == 401:
                raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                         resp.json()['errorMessage']['code'])
            else:
                raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

    def _delete_gfycat(self, _id):
        resp = self.session.delete(f'{Gfypy.ME_ENDPOINT}/gfycats/{_id}', auth=self.bearer_auth)

        if resp.status_code != 204:
            if resp.status_code == 401:
                raise GfypyAuthException(resp.json()['errorMessage']['description'], resp.status_code,
                                         resp.json()['errorMessage']['code'])
            else:
                raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

    def get_user(self, _id):
        resp = self.session.get(f'{Gfypy.USERS_ENDPOINT}/{_id}', auth=self.bearer_auth)

        if resp.status_code != 200:
            raise GfypyApiException(resp.json()['errorMessage'], resp.status_code)

        return User.from_dict(self, resp.json())
