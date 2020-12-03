import asyncio
import inspect
import json
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, urlencode

from gfypy.const import AUTH_ENDPOINT, REDIRECT_URI
from gfypy.exceptions import GfypyException
from gfypy.gfy import Gfy
from gfypy.route import Route
from gfypy.user import User


class Promise:
    def __init__(self, coro):
        self.coro = coro
        self._is_coro = inspect.iscoroutine(coro)

    def __await__(self):
        if self._is_coro:
            return self.coro.__await__()
        return asyncio.sleep(0, result=self.coro).__await__()

    def then(self, later):
        if self._is_coro:

            async def chain():
                value = await self.coro
                return await Promise(later(value))

            return chain()
        else:
            return later(self.coro)


class AuthCallbackRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<h2>You may close this window now!</h2>", "UTF-8"))
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        code = query_components["code"]
        self.server.code = code


class AbstractGfypy:
    MAX_TAGS = 20
    MAX_CHECKS = 30

    def __init__(self, client_id, client_secret, auth_file_path):
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_file_path = Path(auth_file_path)

    def _get_oauth_code(self):
        """
        Gets authorization token
        """
        server = ThreadingHTTPServer(("localhost", 8000), AuthCallbackRequestHandler)
        server.code = None
        server_thread = Thread(target=server.serve_forever)
        server_thread.daemon = False
        server_thread.start()

        params = {
            "client_id": self._client_id,
            "scope": "all",
            "state": "Gfypy",
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
        }

        auth_url = f"{AUTH_ENDPOINT}?{urlencode(params)}"

        webbrowser.open(auth_url)

        while server.code is None:
            time.sleep(1)

        assassin = Thread(target=server.shutdown)
        assassin.daemon = True
        assassin.start()

        return server.code

    def _auth_to_disk(self):
        with open(self._auth_file_path, "w") as auth_file:
            auth_file.write(json.dumps(self._http.creds))

    def _check_upload_status(self, gfy_key):
        return self._http.request(
            Route("GET", "/gfycats/fetch/status/{gfy_key}", gfy_key=gfy_key)
        )

    def get_me(self):
        return Promise(self._http.request(Route("GET", "/me"))).then(
            lambda r: User.from_dict(self._http, r)
        )

    def _get_key(self, title="", tags=None, keep_audio=True, check_duplicate=False):
        tags = tags or []

        if len(tags) > self.MAX_TAGS:
            raise GfypyException(
                f"Too many tags. Supplied {len(tags)}, max. {self.MAX_TAGS}."
            )

        payload = {
            "title": title,
            "tags": tags,
            "keepAudio": keep_audio,
            "noMd5": not check_duplicate,
        }

        return Promise(
            self._http.request(
                Route("POST", "/gfycats"),
                data=json.dumps(payload),
                headers={"content-type": "application/json"},
            )
        ).then(lambda r: r["gfyname"])

    def get_user_feed(self, user_id, **kwargs):
        raise NotImplementedError

    def get_own_feed(self, **kwargs):
        return self.get_user_feed(**kwargs)

    def get_gfycat(self, _id):
        return Promise(self._http.request(Route("GET", "/gfycats/{id}", id=_id))).then(
            lambda r: Gfy.from_dict(self._http, r["gfyItem"])
        )

    def get_user(self, _id):
        return Promise(self._http.request(Route("GET", "/users/{id}", id=_id))).then(
            lambda r: User.from_dict(self._http, json.loads(r))
        )
