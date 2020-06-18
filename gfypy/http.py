import requests
from tqdm import tqdm

from .exceptions import GfypyAuthException, GfypyApiException
from .gfy import Gfy
from .route import Route


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class HttpClient:
    def __init__(self):
        self._session = requests.Session()
        self._auth = None

    def request(self, route, **kwargs):
        no_auth = kwargs.pop('no_auth') if 'no_auth' in kwargs else False

        if self._auth is not None and not no_auth:
            resp = self._session.request(route.method, route.url, **kwargs, auth=self._auth)
        else:
            resp = self._session.request(route.method, route.url, **kwargs)

        content_type = resp.headers.get('content-type')

        if content_type == 'application/json':
            content = resp.json()
        else:
            content = resp.text

        if 200 <= resp.status_code < 300:
            return content
        elif resp.status_code in [401, 403]:
            if 'message' in content:
                raise GfypyAuthException(content['message'], resp.status_code, None)
            else:
                raise GfypyAuthException(content['errorMessage']['description'], resp.status_code,
                                         content['errorMessage']['code'])
        else:
            raise GfypyApiException(content['errorMessage'], resp.status_code)

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, token):
        self._auth = BearerAuth(token)

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
            resp = self.request(route, params={'count': 100, 'cursor': cursor})

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
