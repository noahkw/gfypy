import asyncio
from gfypy import AsyncGfypy, Gfypy
from conf import CLIENT_ID, CLIENT_SECRET
import time
import json


async def tests():
    gfypy = AsyncGfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    await gfypy.authenticate()

    # gfy = await gfypy.get_gfycat('fearlesswiltedafricancivet')
    # print(gfy['likes'])
    # user = await gfypy.get_user('bjh0329')
    # print(user['views'])

    # start = time.time()
    # gfycats = await gfypy.get_own_feed(limit=-1)
    # end = time.time()
    # print(f'{end - start}s elapsed')
    # print(len(gfycats))
    # me_ = await gfypy.get_me()
    # print(me_)
    # key = await gfypy._get_key('asd')
    # print(key)

    # gfys = await gfypy.get_own_feed(limit=-1)

    # print(len(gfys))

    gfy = await gfypy.get_gfycat('leafydeficientduiker')
    await gfy.set_title('180818 Red Velvet Seulgi Pikachu hat')

    gfy = await gfypy.get_gfycat('leafydeficientduiker')
    print(gfy.title)

    await gfypy.close()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(tests())

    # # sync
    # gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    # gfypy.authenticate()
    # me = gfypy.get_me()
    # print(me)
    #
    # gfys = gfypy.get_own_feed(limit=-1)
    # print(len(gfys))
