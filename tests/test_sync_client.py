import logging
import sys
import warnings

from conf import CLIENT_ID, CLIENT_SECRET
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
