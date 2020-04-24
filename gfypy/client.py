import requests
import webbrowser
import json


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


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

    def _get_oauth_token(self):
        """
        Gets authorization token
        """
        auth_url = f'{Gfypy.AUTH_ENDPOINT}?client_id={self.client_id}' \
                   f'&scope=all' \
                   f'&state=Gfypy' \
                   f'&response_type=token' \
                   f'&redirect_uri={Gfypy.REDIRECT_URI}'
        webbrowser.open(auth_url)

        print('Please paste the entire URL after clicking "OK": ')
        self.access_token = input()
        self.auth = BearerAuth(self.access_token)

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
