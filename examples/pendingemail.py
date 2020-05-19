from gfypy.client import Gfypy
from conf import CLIENT_ID, CLIENT_SECRET
import time
import json
import os


def pendingcheck():
    """
    go through own feed, write a text file with all gfys stuck on pending
    """
    start = time.time()
    gfycats = gfypy.get_own_feed(limit=10000, gatekeeper=5)
    end = time.time()
    print(f'{end - start}s elapsed')
    tosend = "Hi,\n\nThese gfys are stuck on pending review\n\n"

    for i in range(len(gfycats)):
        tosend += f"{i+1} https://www.gfycat.com/{gfycats[i]['gfyId']}\n"
    tosend += "\nThanks"

    with open('gfycatemail.txt', 'w') as f:
        f.write(tosend)

            
if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    gfypy.authenticate()
    #gfypy.initial_auth()
    #gfypy._auth_to_disk()
    pendingcheck()
