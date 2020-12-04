import json
import logging
import time

from tqdm import tqdm

from gfypy.client.abstract_client import AbstractGfypy
from gfypy.const import GFYCAT_URL, FILEDROP_ENDPOINT
from gfypy.exceptions import GfypyAuthException, GfypyApiException
from gfypy.gfy import Gfy
from gfypy.http import SyncHttpClient
from gfypy.route import Route, CustomRoute

logger = logging.getLogger(__name__)


class Gfypy(AbstractGfypy):
    def __init__(self, client_id, client_secret, auth_file_path):
        super().__init__(client_id, client_secret, auth_file_path)
        self._http = SyncHttpClient(client_id, client_secret)

    def authenticate(self):
        if not self._auth_file_path.is_file():
            logger.info(
                'Credentials file "%s" does not exist. Creating it now.',
                self._auth_file_path,
            )
            with open(self._auth_file_path, "w") as auth_file:
                auth_file.write(json.dumps(self._http.creds))

        with open(self._auth_file_path, "r") as auth_file:
            self._http.creds = json.loads(auth_file.read())

            try:
                self._http.refresh_oauth_token(refresh=False)
            except GfypyAuthException as e:
                if e.code == "InvalidRefreshToken":
                    self._initial_auth()
                    self._auth_to_disk()
                else:
                    raise

    def close(self):
        self._http.close()

    def _initial_auth(self):
        self._http.get_oauth_token(self._get_oauth_code())

    def upload_from_file(
        self,
        filename,
        title="",
        tags=None,
        keep_audio=True,
        check_duplicate=False,
        check_upload=True,
    ):
        tags = tags or []

        key = self._get_key(title, tags, keep_audio, check_duplicate)
        payload = {"key": key}

        with open(filename, "rb") as file:
            files = {"file": (key, file.read())}

        self._http.request(
            CustomRoute("POST", FILEDROP_ENDPOINT),
            data=payload,
            files=files,
            no_auth=True,
        )

        if check_upload:
            status = self._check_upload_status(key)

            progress = tqdm(total=self.MAX_CHECKS)
            num_checks = 0
            while status["task"] != "complete":
                if num_checks > self.MAX_CHECKS:
                    # the gfycat was likely uploaded correctly, but gfycat is not sending 'task': 'complete'
                    break
                status = self._check_upload_status(key)
                progress.update(1)
                num_checks += 1
                time.sleep(3)

            progress.close()

            try:
                gfy = self.get_gfycat(key)

                logger.info(
                    "\n%s has been uploaded as %s/%s.", filename, GFYCAT_URL, key
                )
                return gfy
            except GfypyApiException:
                logger.info(
                    "\n%s has probably been uploaded as %s/%s, but the check was unsuccessful.",
                    filename,
                    GFYCAT_URL,
                    key,
                )
                return None
        else:
            logger.info(
                "\n%s has been uploaded as %s/%s; checks have been skipped.",
                filename,
                GFYCAT_URL,
                key,
            )

    def get_followers(self, fetch_userdata=False):
        resp = self._http.request(Route("GET", "/me/followers"))

        if not fetch_userdata:
            return resp["followers"]
        else:
            users = []
            for follower in resp["followers"]:
                user = self.get_user(follower["follower_id"])
                user["follow_date"] = follower["follow_date"]
                users.append(user)

            return users

    def get_user_feed(
        self, user_id=None, limit=100, sort_by=None, desc=True, filter_predicate=None
    ):
        if limit % 100 != 0 and limit >= 0:
            print("Limit needs to be divisible by 100. Rounding up.")

        gfycats = []
        i = 0
        cursor = ""

        if user_id is None:
            route = Route("GET", "/me/gfycats")
        else:
            route = Route("GET", "/users/{id}/gfycats", id=user_id)

        progress = tqdm(total=limit)

        while i < limit or limit < 0:
            resp = self._http.request(route, params={"count": 100, "cursor": cursor})

            cursor = resp["cursor"]
            new_gfys = Gfy.from_dict_list(self, resp["gfycats"])
            gfycats.extend(new_gfys)
            progress.update(len(new_gfys))

            if not cursor:
                print("Got no new entries from Gfycat. Stopping here.")
                break

            i = len(gfycats)

        progress.close()

        if filter_predicate:
            gfycats = [g for g in gfycats if filter_predicate(g)]

        if sort_by:
            gfycats = sorted(
                gfycats, key=lambda gfy: getattr(gfy, sort_by), reverse=desc
            )

        return gfycats
