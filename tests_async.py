import asyncio
from gfypy import AsyncGfypy, Gfypy
from conf import CLIENT_ID, CLIENT_SECRET
import time


async def tests():
    gfypy = AsyncGfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
    await gfypy.authenticate()

    # gfy = await gfypy.get_gfycat('fearlesswiltedafricancivet')
    # print(gfy['likes'])
    # user = await gfypy.get_user('bjh0329')
    # print(user['views'])

    start = time.time()
    gfycats = await gfypy.get_own_feed(limit=-1)
    end = time.time()
    print(f'{end - start}s elapsed')
    print(len(gfycats))

    await gfypy.close()

if __name__ == '__main__':


    # start = time.time()
    # gfycats = gfypy.get_own_feed(limit=2000)
    # end = time.time()
    # print(f'{end - start}s elapsed')
    # print(len(gfycats))

    # print(user.get_albums())
    # print(gfypy.get_own_albums())
    asyncio.get_event_loop().run_until_complete(tests())