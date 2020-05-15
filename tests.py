from gfypy.client import Gfypy
from conf import CLIENT_ID, CLIENT_SECRET

if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET)
    gfypy.initial_auth()
    # gfypy.get_key('this is a test', ['tag', 'tag2', 'tag with 한글'])
    # gfypy.upload_from_file('this is a test', ['tag', 'tag2', 'tag with 한글'], 'unamused_fin_longest.gif')
