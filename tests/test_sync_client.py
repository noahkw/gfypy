import logging
import sys
import warnings

from conf_test import CLIENT_ID, CLIENT_SECRET
from gfypy import Gfypy

import unittest

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


class TestSyncGfypy(unittest.TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger("gfypy")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )
        logger.addHandler(handler)

        self.gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, "../creds.json")
        self.gfypy.authenticate()

    def tearDown(self) -> None:
        self.gfypy.close()

    def test_get_own_feed(self):
        gfys = self.gfypy.get_own_feed(limit=-1)
        self.assertGreater(len(gfys), 1)

    def test_upload_from_file(self):
        title = "This is a test upload"

        # Example file source: https://file-examples.com/index.php/sample-video-files/sample-mp4-files/
        gfy = self.gfypy.upload_from_file(
            "example.mp4",
            title=title,
            tags=["Test", "Upload from file", "Gfypy"],
            keep_audio=True,
        )
        self.assertEqual(gfy.title, title)

    def test_get_me(self):
        username = "gfycat_ux_goat"

        user = self.gfypy.get_me()
        self.assertEqual(user.username, username)

        # for backwards compatibility with dict-like user objects
        self.assertEqual(user["username"], username)

    def test_get_gfycat(self):
        gfy = self.gfypy.get_gfycat("inexperiencedsneakyacouchi")

        self.assertEqual(gfy.title, "This is a test upload")
