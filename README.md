# gfypy ![Python package](https://github.com/noahkw/gfypy/workflows/Python%20package/badge.svg) [![PyPI version](https://badge.fury.io/py/gfypy.svg)](https://badge.fury.io/py/gfypy)

Install the latest release from PyPi: 

`python -m pip install gfypy` 

Or install the latest development version from source: 

`python -m pip install -U git+https://github.com/noahkw/gfypy`

## Basic Usage

Request API credentials at https://developers.gfycat.com/signup/#/apiform. Make sure to add `http://localhost:8000/callback` as a redirect URI or the OAuth authentication will fail.

```python
from gfypy import Gfypy

gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, './creds.json')
gfypy.authenticate()

# getting info on a single gfycat
gfycat_info = gfypy.get_gfycat('apprehensivefixedgermanpinscher')

# creating a new gfycat via file upload
gfypy.upload_from_file(f'test_video.webm', title='This is a test video. Don\'t upvote.', 
                                           tags=['testing stuff', 'gfycat is awesome'])
```
