# gfypy

This project is not on PyPi as of yet, but it may be installed directly from source: 

`python -m pip install -U git+https://github.com/noahkw/gfypy`

## Basic Usage

Request API credentials at https://developers.gfycat.com/signup/#/apiform. Make sure to add `http://localhost:8000` as a redirect URI or the OAuth authentication will fail.

```
from gfypy.client import Gfypy

gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
gfypy.authenticate()

# getting info on a single gfycat
gfycat_info = gfypy.get_gfycat('apprehensivefixedgermanpinscher')

# creating a new gfycat via file upload
gfypy.upload_from_file(f'test_video.webm', title='This is a test video. Don\'t upvote.', 
                                           tags=['testing stuff', 'gfycat is awesome'])
```
