from gfypy import Gfypy
from conf import CLIENT_ID, CLIENT_SECRET
import time

if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    gfypy.authenticate()

    start = time.time()
    gfycats = gfypy.get_own_feed(limit=2000)
    end = time.time()
    print(f'{end - start}s elapsed')
    print(len(gfycats))
