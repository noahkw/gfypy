from gfypy.client import Gfypy
from conf import CLIENT_ID, CLIENT_SECRET
import time

if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    gfypy.authenticate()
    # gfypy.initial_auth()
    # gfypy._auth_to_disk()

    start = time.time()
    gfycats = gfypy.get_own_feed(limit=2000)
    end = time.time()
    print(f'{end - start}s elapsed')
    print(len(gfycats))

    # gfypy.get_key('this is a test', ['tag', 'tag2', 'tag with 한글'])
    # gfypy.upload_from_file('this is a test', ['tag', 'tag2', 'tag with 한글'], 'unamused_fin_longest.gif')
