import json

from .route import Route


class Gfy(dict):
    PROPERTIES = ['title', 'tags', 'languageCategories', 'domainWhitelist', 'geoWhitelist', 'published', 'nsfw',
                  'gatekeeper', 'mp4Url', 'gifUrl', 'webmUrl', 'webpUrl', 'mobileUrl', 'mobilePosterUrl',
                  'thumb100PosterUrl', 'miniUrl', 'gif100px', 'miniPosterUrl', 'max5mbGif', 'max2mbGif', 'max1mbGif',
                  'posterUrl', 'views', 'description', 'hasTransparency', 'hasAudio', 'gfyId', 'gfyName',
                  'width', 'height', 'frameRate', 'numFrames', 'mp4Size', 'webmSize', 'createDate', 'source']

    INT_PROPERTIES = ['likes', 'dislikes', 'gfyNumber']
    OPTIONAL_PROPERTIES = ['gfySlug', 'md5', 'rating', 'avgColor']

    def __init__(self, http, **kwargs):
        super().__init__()
        self._copy_properties(kwargs)
        self._http = http

    def _copy_properties(self, source):
        for p in self.PROPERTIES:
            self[p] = source[p]

        for p in self.INT_PROPERTIES:
            self[p] = int(source[p])

        for p in self.OPTIONAL_PROPERTIES:
            self[p] = source[p] if p in source else None

    @staticmethod
    def from_dict(http, source):
        return Gfy(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [Gfy.from_dict(http, gfy) for gfy in source]

    def _refetch(self):
        resp = self._http.request(Route('GET', '/gfycats/{id}', id=self['gfyId']))
        refetched_gfy = self.from_dict(self._http, resp['gfyItem'])
        self._copy_properties(refetched_gfy)

    def set_title(self, new_title):
        payload = {
            'value': new_title
        }

        self._http.request(Route('PUT', '/me/gfycats/{id}/title', id=self['gfyId']), data=json.dumps(payload))
        self._refetch()

    def delete_title(self):
        self._http.request(Route('DELETE', '/me/gfycats/{id}/title', id=self['gfyId']))
        self._refetch()

    def delete(self):
        self._http.request(Route('DELETE', '/me/gfycats/{id}', id=self['gfyId']))
        self._refetch()
