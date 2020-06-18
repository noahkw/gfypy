class User(dict):
    PROPERTIES = ['views', 'verified', 'iframeProfileImageVisible', 'url', 'userid', 'username', 'following',
                  'followers', 'createDate']

    OPTIONAL_PROPERTIES = ['description', 'name', 'publishedGfycats', 'profileImageUrl']

    def __init__(self, http, **kwargs):
        super().__init__()
        self._copy_properties(kwargs)
        self._http = http

    def _copy_properties(self, source):
        for p in self.PROPERTIES:
            self[p] = source[p]

        for p in self.OPTIONAL_PROPERTIES:
            self[p] = source[p] if p in source else None

    @staticmethod
    def from_dict(http, source):
        return User(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [User.from_dict(http, user) for user in source]
