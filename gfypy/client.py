import json
import webbrowser
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse

import requests


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
    AUTH_ENDPOINT = 'https://gfycat.com/oauth/authorize'
    ACCESS_TOKEN_ENDPOINT = 'https://api.gfycat.com/v1/oauth/token'
    REDIRECT_URI = 'http://localhost:8000/callback'
    GFYCATS_ENDPOINT = 'https://api.gfycat.com/v1/gfycats'
    FILEDROP_ENDPOINT = 'https://filedrop.gfycat.com/'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.auth = None

    def initial_auth(self):
        self._get_oauth_token(self._get_oauth_code())
        print(self.auth)

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

        resp = requests.post(Gfypy.ACCESS_TOKEN_ENDPOINT, data=json.dumps(payload),
                             headers={'content-type': 'application/json'})

        self.auth = BearerAuth(resp.json()['access_token'])

    def _get_key(self, title=None, tags=None):
        payload = {
            'title': title,
            'tags': tags
        }

        resp = requests.post(Gfypy.GFYCATS_ENDPOINT, data=json.dumps(payload),
                             auth=self.auth, headers={'content-type': 'application/json'})
        print(resp.json())
        return resp.json()['gfyname']

    def upload_from_file(self, title=None, tags=None, filename=None):
        """
        Upload a local file to gfycat
        :param title:
        :param tags:
        :param filename:
        :return:
        """
        key = self._get_key(title, tags)
        payload = {
            'key': key
        }
        files = {
            'file': (key, open(filename, 'rb').read())
        }
        resp = requests.post(Gfypy.FILEDROP_ENDPOINT, data=payload, files=files)

        print(resp.status_code)
