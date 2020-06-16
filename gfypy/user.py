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
