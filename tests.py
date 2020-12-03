import logging
import sys
import time

from conf import CLIENT_ID, CLIENT_SECRET
from gfypy import Gfypy

if __name__ == '__main__':
    logger = logging.getLogger("gfypy")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)

    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    gfypy.authenticate()

    start = time.time()
    gfycats = gfypy.get_own_feed(limit=2000)
    end = time.time()
    print(f'{end - start}s elapsed')
    print(len(gfycats))
