class Gfy(dict):
    PROPERTIES = ['title', 'tags', 'languageCategories', 'domainWhitelist', 'geoWhitelist', 'published', 'nsfw',
                  'gatekeeper', 'mp4Url', 'gifUrl', 'webmUrl', 'webpUrl', 'mobileUrl', 'mobilePosterUrl',
                  'thumb100PosterUrl', 'miniUrl', 'gif100px', 'miniPosterUrl', 'max5mbGif', 'max2mbGif', 'max1mbGif',
                  'posterUrl', 'views', 'description', 'hasTransparency', 'hasAudio', 'gfyId', 'gfyName', 'avgColor',
                  'width', 'height', 'frameRate', 'numFrames', 'mp4Size', 'webmSize', 'createDate', 'source']

    INT_PROPERTIES = ['likes', 'dislikes', 'gfyNumber']
    OPTIONAL_PROPERTIES = ['gfySlug', 'md5', 'rating']

    def __init__(self, client, **kwargs):
        super().__init__()
        self._copy_properties(kwargs)
        self.client = client

    def _copy_properties(self, source):
        for p in Gfy.PROPERTIES:
            self[p] = source[p]

        for p in Gfy.INT_PROPERTIES:
            self[p] = int(source[p])

        for p in Gfy.OPTIONAL_PROPERTIES:
            self[p] = source[p] if p in source else None

    @staticmethod
    def from_dict(client, source):
        return Gfy(client, **source)

    @staticmethod
    def from_dict_list(client, source):
        return [Gfy.from_dict(client, gfy) for gfy in source]

    def _refetch(self):
        refetched_gfy = self.client.get_gfycat(self['gfyId'])
        self._copy_properties(refetched_gfy)

    def set_title(self, new_title):
        self.client._set_gfycat_title(self['gfyId'], new_title)
        self._refetch()

    def delete_title(self):
        self.client._delete_gfycat_title(self['gfyId'])
        self._refetch()

    def delete(self):
        self.client._delete_gfycat(self['gfyId'])
        self._refetch()


class User(dict):
    PROPERTIES = ['views', 'verified', 'iframeProfileImageVisible', 'url', 'userid', 'username', 'following',
                  'followers', 'description', 'profileImageUrl', 'name', 'publishedGfycats', 'createDate']

    def __init__(self, client, **kwargs):
        super().__init__()
        self._copy_properties(kwargs)
        self.client = client

    def _copy_properties(self, source):
        for p in User.PROPERTIES:
            self[p] = source[p]

    @staticmethod
    def from_dict(client, source):
        return User(client, **source)
