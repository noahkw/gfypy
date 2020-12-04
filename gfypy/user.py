import typing
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User(dict):
    def __init__(self, http, **kwargs):
        super().__init__(kwargs)
        self._http = http
        self._source = kwargs

        # explicit cast to int required because the API sometimes returns a str
        self.following: int = (
            int(kwargs.pop("following")) if "following" in kwargs else None
        )
        self.followers: int = (
            int(kwargs.pop("followers")) if "followers" in kwargs else None
        )
        self.views: int = int(kwargs.pop("views")) if "views" in kwargs else None
        self.create_date: datetime = (
            datetime.fromtimestamp(int(kwargs.pop("createDate")))
            if "createDate" in kwargs
            else None
        )
        self.published_gfycats: int = (
            int(kwargs.pop("publishedGfycats"))
            if "publishedGfycats" in kwargs
            else None
        )
        self.total_gfycats: int = (
            int(kwargs.pop("totalGfycats")) if "totalGfycats" in kwargs else None
        )
        self.total_bookmarks: int = (
            int(kwargs.pop("totalBookmarks")) if "totalBookmarks" in kwargs else None
        )
        self.total_albums: int = (
            int(kwargs.pop("totalAlbums")) if "totalAlbums" in kwargs else None
        )
        self.published_albums: int = (
            int(kwargs.pop("publishedAlbums")) if "publishedAlbums" in kwargs else None
        )

        self.subscription: int = kwargs.pop("subscription", None)
        self.verified: bool = kwargs.pop("verified", None)
        self.iframe_profile_image_visible: bool = kwargs.pop(
            "iframeProfileImageVisible", None
        )
        self.url: str = kwargs.pop("url", None)
        self.userid: str = kwargs.pop("userid", None)
        self.username: str = kwargs.pop("username", None)
        self.description: str = kwargs.pop("description", None)
        self.name: str = kwargs.pop("name", None)
        self.profile_image_url: str = kwargs.pop("profileImageUrl", None)
        self.email: str = kwargs.pop("email", None)
        self.canonical_username: str = kwargs.pop("canonicalUsername", None)
        self.email_verified: bool = kwargs.pop("emailVerified", None)
        self.viewing_preference: int = kwargs.pop("viewingPreference", None)
        self.domain_whitelist: typing.List[typing.Any] = kwargs.pop(
            "domainWhitelist", []
        )
        self.geo_whitelist: typing.List[typing.Any] = kwargs.pop("geoWhitelist", [])

    @staticmethod
    def from_dict(http, source):
        return User(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [User.from_dict(http, user) for user in source]
