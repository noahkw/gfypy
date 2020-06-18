import json
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, urlencode

from tqdm import tqdm

from .exceptions import GfypyAuthException
from .gfy import Gfy
from .http import HttpClient, Route, CustomRoute
from .user import User


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
    FILEDROP_ENDPOINT = 'https://filedrop.gfycat.com/'
    AUTH_ENDPOINT = 'https://gfycat.com/oauth/authorize'

    REDIRECT_URI = 'http://localhost:8000/callback'

    def __init__(self, client_id, client_secret, auth_file_path):
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_file_path = Path(auth_file_path)
        self._auth = {
            'access_token': None,
            'expires_in': None,
            'refresh_token': None,
            'refresh_token_expires_in': None,
            'resource_owner': None
        }
        self._http = HttpClient()

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

    def _get_oauth_code(self):
        """
        Gets authorization token
        """
        server = ThreadingHTTPServer(('localhost', 8000), AuthCallbackRequestHandler)
        server.code = None
        server_thread = Thread(target=server.serve_forever)
        server_thread.daemon = False
        server_thread.start()

        params = {
            'client_id': self._client_id,
            'scope': 'all',
            'state': 'Gfypy',
            'response_type': 'code',
            'redirect_uri': self.REDIRECT_URI
        }

        auth_url = f'{Gfypy.AUTH_ENDPOINT}?{urlencode(params)}'

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
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': Gfypy.REDIRECT_URI
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

    def _auth_to_disk(self):
        with open(self._auth_file_path, 'w') as auth_file:
            auth_file.write(json.dumps(self._auth))

    def _get_key(self, title='', tags=[], keep_audio=True, check_duplicate=False):
        payload = {
            'title': title,
            'tags': tags,
            'keepAudio': keep_audio,
            'noMd5': not check_duplicate
        }

        resp = self._http.request(Route('POST', '/gfycats'), data=json.dumps(payload),
                                  headers={'content-type': 'application/json'})

        return resp['gfyname']

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

        self._http.request(CustomRoute('POST', self.FILEDROP_ENDPOINT), data=payload, files=files, no_auth=True)
        status = self._check_upload_status(key)

        while status['task'] != 'complete':
            time.sleep(3)
            status = self._check_upload_status(key)
            print(status)

        print(f'{filename} has been uploaded as {Gfypy.GFYCAT_URL}/{key}.')

        gfy = self.get_gfycat(key)
        return gfy

    def _check_upload_status(self, gfy_key):
        resp = self._http.request(Route('GET', '/gfycats/fetch/status/{gfy_key}', gfy_key=gfy_key))
        return resp

    def get_user_feed(self, user_id=None, limit=20, sort_by=None, desc=True, filter_predicate=None):
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
            resp = self._http.request(route, params={'count': 100, 'cursor': cursor})

            cursor = resp['cursor']
            new_gfys = Gfy.from_dict_list(self._http, resp['gfycats'])
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

    def get_own_feed(self, limit=20, sort_by=None, desc=True, filter_predicate=None):
        return self.get_user_feed(limit=limit, sort_by=sort_by, desc=desc, filter_predicate=filter_predicate)

    def get_gfycat(self, _id):
        resp = self._http.request(Route('GET', '/gfycats/{id}', id=_id))
        return Gfy.from_dict(self._http, resp['gfyItem'])

    def get_user(self, _id):
        resp = self._http.request(Route('GET', '/users/{id}', id=_id))
        # Gfycat returns the wrong content type here. Thus, we need to parse the string explicitly.
        return User.from_dict(self._http, json.loads(resp))
