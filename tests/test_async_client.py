import os
import time
import warnings

from conf_test import CLIENT_ID, CLIENT_SECRET
from gfypy import AsyncGfypy

import unittest

from tests.test_sync_client import setup_logging

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)


class TestAsyncGfypy(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.logger = setup_logging()

        self.gfypy = AsyncGfypy(CLIENT_ID, CLIENT_SECRET, "../creds.json")
        await self.gfypy.authenticate()

    async def asyncTearDown(self) -> None:
        await self.gfypy.close()

    async def test_get_own_feed(self):
        gfys = await self.gfypy.get_own_feed(limit=-1)
        self.assertGreater(len(gfys), 1)

    async def test_upload_from_file(self):
        title = "This is a test upload"

        # Example file source: https://file-examples.com/index.php/sample-video-files/sample-mp4-files/
        gfy = await self.gfypy.upload_from_file(
            "example.mp4",
            title=title,
            tags=["Test", "Upload from file", "Gfypy"],
            keep_audio=True,
        )
        self.assertEqual(gfy.title, title)

    async def test_get_me(self):
        username = "gfycat_ux_goat"

        user = await self.gfypy.get_me()
        self.assertEqual(user.username, username)

        # for backwards compatibility with dict-like user objects
        self.assertEqual(user["username"], username)

    async def test_get_gfycat(self):
        gfy = await self.gfypy.get_gfycat("inexperiencedsneakyacouchi")

        self.assertEqual(gfy.title, "This is a test upload")


class TestAsyncGfypyAuth(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.logger = setup_logging()
        self.creds_file = f"./creds_{time.time()}.json"

    async def asyncTearDown(self) -> None:
        self.logger.info("Cleaning up")
        os.remove(self.creds_file)

    async def test_headless_auth(self):
        gfypy = AsyncGfypy(CLIENT_ID, CLIENT_SECRET, self.creds_file, headless=True)
        await gfypy.authenticate()
        await gfypy.close()
