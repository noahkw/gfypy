import logging
import sys
import warnings

from conf import CLIENT_ID, CLIENT_SECRET
from gfypy import AsyncGfypy

import unittest

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


class TestAsyncGfypy(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        logger = logging.getLogger("gfypy")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )
        logger.addHandler(handler)

        self.gfypy = AsyncGfypy(CLIENT_ID, CLIENT_SECRET, "../creds.json")
        await self.gfypy.authenticate()

    async def asyncTearDown(self) -> None:
        await self.gfypy.close()

    async def test_get_own_feed(self):
        gfys = await self.gfypy.get_own_feed(limit=-1)
        self.assertGreater(len(gfys), 1)
