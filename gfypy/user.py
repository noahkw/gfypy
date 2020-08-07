from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class User(dict):
    views: int
    verified: bool
    iframe_profile_image_visible: bool
    url: str
    userid: str
    username: str
    following: int
    followers: int
    create_date: datetime
    description: str
    name: str
    published_gfycats: int
    profile_image_url: str
    email: str
    canonical_username: str
    email_verified: bool
    total_gfycats: int
    total_bookmarks: int
    total_albums: int
    published_albums: int
    subscription: str
    viewing_preference: str
    domain_whitelist: List
    geo_whitelist: List

    def __init__(self, http, **kwargs):
        super().__init__(kwargs)
        self._http = http
        self._source = kwargs

        # explicit cast to int required because the API sometimes returns a str
        self.following = int(kwargs.pop('following')) if 'following' in kwargs else None
        self.followers = int(kwargs.pop('followers')) if 'followers' in kwargs else None
        self.views = int(kwargs.pop('views')) if 'views' in kwargs else None
        self.create_date = datetime.fromtimestamp(int(kwargs.pop('createDate'))) if 'createDate' in kwargs else None
        self.published_gfycats = int(kwargs.pop('publishedGfycats')) if 'publishedGfycats' in kwargs else None
        self.total_gfycats = int(kwargs.pop('totalGfycats')) if 'totalGfycats' in kwargs else None
        self.total_bookmarks = int(kwargs.pop('totalBookmarks')) if 'totalBookmarks' in kwargs else None
        self.total_albums = int(kwargs.pop('totalAlbums')) if 'totalAlbums' in kwargs else None
        self.published_albums = int(kwargs.pop('publishedAlbums')) if 'publishedAlbums' in kwargs else None

        self.subscription = kwargs.pop('subscription', None)
        self.verified = kwargs.pop('verified', None)
        self.iframe_profile_image_visible = kwargs.pop('iframeProfileImageVisible', None)
        self.url = kwargs.pop('url', None)
        self.userid = kwargs.pop('userid', None)
        self.username = kwargs.pop('username', None)
        self.description = kwargs.pop('description', None)
        self.name = kwargs.pop('name', None)
        self.profile_image_url = kwargs.pop('profileImageUrl', None)
        self.email = kwargs.pop('email', None)
        self.canonical_username = kwargs.pop('canonicalUsername', None)
        self.email_verified = kwargs.pop('emailVerified', None)
        self.viewing_preference = kwargs.pop('viewingPreference', None)
        self.domain_whitelist = kwargs.pop('domainWhitelist', None)
        self.geo_whitelist = kwargs.pop('geoWhitelist', None)

    @staticmethod
    def from_dict(http, source):
        return User(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [User.from_dict(http, user) for user in source]
