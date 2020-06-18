import time

from conf import CLIENT_ID, CLIENT_SECRET
from gfypy import Gfypy
from gfypy import is_pending


def pending_check():
    """
    go through own feed, write a text file with all gfys stuck on pending
    """
    start = time.time()
    gfycats = gfypy.get_own_feed(limit=10000, filter_predicate=is_pending)
    end = time.time()
    print(f'{end - start}s elapsed')
    to_send = "Hi,\n\nThese gfys are stuck on pending review\n\n"

    for i in range(len(gfycats)):
        to_send += f"{i + 1} https://www.gfycat.com/{gfycats[i]['gfyId']}\n"
    to_send += "\nThanks"

    with open('gfycatemail.txt', 'w') as f:
        f.write(to_send)


if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, '../creds.json')
    gfypy.authenticate()

    pending_check()
