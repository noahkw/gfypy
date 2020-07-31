from urllib.parse import urlencode, quote

from conf import CLIENT_ID, CLIENT_SECRET
from gfypy import Gfypy, is_pending

GFYCAT_SUPPORT_EMAIL = 'support@gfycat.com'
SUBJECT = 'Gfys stuck on pending review'


def pending_check():
    """
    go through own feed, create a mailto link with all gfys stuck on pending
    """
    gfycats = gfypy.get_own_feed(limit=-1, filter_predicate=is_pending)
    body = "Hi,\n\nThese gfys are stuck on pending review:\n\n"

    body += '\n'.join([Gfypy.GFYCAT_URL + '/' + gfy['gfyId'] for gfy in gfycats])
    body += "\n\nThanks"

    params = {
        'subject': SUBJECT,
        'body': body
    }

    mailto = f'mailto:{GFYCAT_SUPPORT_EMAIL}?{urlencode(params, quote_via=quote)}'
    print(mailto)


if __name__ == '__main__':
    gfypy = Gfypy(CLIENT_ID, CLIENT_SECRET, '../creds.json')
    gfypy.authenticate()

    pending_check()
