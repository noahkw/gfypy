import json
from datetime import datetime

from .route import Route

from dataclasses import dataclass
import typing


@dataclass
class ContentUrl:
    def __init__(self, **kwargs):
        self.url: str = kwargs.pop("url", None)
        self.size: int = kwargs.pop("size", None)
        self.height: int = kwargs.pop("height", None)
        self.width: int = kwargs.pop("width", None)


@dataclass
class UserData:
    def __init__(self, **kwargs):
        self.name: str = kwargs.pop("name", None)
        self.profile_image_url: str = kwargs.pop("profileImageUrl", None)
        self.url: str = kwargs.pop("url", None)
        self.username: str = kwargs.pop("username", None)
        self.followers: int = kwargs.pop("followers", None)
        self.subscription: int = kwargs.pop("subscription", None)
        self.following: int = kwargs.pop("following", None)
        self.profile_url: str = kwargs.pop("profileUrl", None)
        self.views: int = kwargs.pop("views", None)
        self.verified: bool = kwargs.pop("verified", None)


@dataclass
class ContentUrls:
    def __init__(self, **kwargs):
        self.max2_mb_gif = (
            ContentUrl(**kwargs.pop("max2mbGif")) if "max2mbGif" in kwargs else None
        )
        self.webp = ContentUrl(**kwargs.pop("webp")) if "webp" in kwargs else None
        self.max1_mb_gif = (
            ContentUrl(**kwargs.pop("max1mbGif")) if "max1mbGif" in kwargs else None
        )
        self._100_px_gif = (
            ContentUrl(**kwargs.pop("100pxGif")) if "100pxGif" in kwargs else None
        )
        self.mobile_poster = (
            ContentUrl(**kwargs.pop("mobilePoster"))
            if "mobilePoster" in kwargs
            else None
        )
        self.mp4 = ContentUrl(**kwargs.pop("mp4")) if "mp4" in kwargs else None
        self.webm = ContentUrl(**kwargs.pop("webm")) if "webm" in kwargs else None
        self.max5_mb_gif = (
            ContentUrl(**kwargs.pop("max5mbGif")) if "max5mbGif" in kwargs else None
        )
        self.large_gif = (
            ContentUrl(**kwargs.pop("largeGif")) if "largeGif" in kwargs else None
        )
        self.mobile = ContentUrl(**kwargs.pop("mobile")) if "mobile" in kwargs else None


@dataclass
class Gfy(dict):
    def __init__(self, http, **kwargs):
        super().__init__(kwargs)
        self._http = http
        self._source = kwargs

        self.content_urls = ContentUrls(**kwargs.pop("content_urls", {}))
        self.user_data = UserData(**kwargs.pop("userData", {}))

        # explicit cast to int required because the API sometimes returns a str
        self.likes: int = int(kwargs.pop("likes", 0))
        self.dislikes: int = int(kwargs.pop("dislikes", 0))
        self.gfy_number: int = int(kwargs.pop("gfyNumber", 0))

        self.title = kwargs.pop("title", None)
        self.tags: typing.Set[str] = set(kwargs.pop("tags", None))
        self.language_categories: typing.List[typing.Any] = kwargs.pop(
            "languageCategories", []
        )
        self.domain_whitelist: typing.List[typing.Any] = kwargs.pop(
            "domainWhitelist", []
        )
        self.geo_whitelist: typing.List[typing.Any] = kwargs.pop("geoWhitelist", [])
        self.published: int = kwargs.pop("published", None)
        self.nsfw: int = kwargs.pop("nsfw", None)
        self.gatekeeper: int = kwargs.pop("gatekeeper", None)
        self.mp4_url: str = kwargs.pop("mp4Url", None)
        self.gif_url: str = kwargs.pop("gifUrl", None)
        self.webm_url: str = kwargs.pop("webmUrl", None)
        self.webp_url: str = kwargs.pop("webpUrl", None)
        self.mobile_url: str = kwargs.pop("mobileUrl", None)
        self.mobile_poster_url: str = kwargs.pop("mobilePosterUrl", None)
        self.extra_lemmas: str = kwargs.pop("extraLemmas", None)
        self.thumb100_poster_url: str = kwargs.pop("thumb100PosterUrl", None)
        self.mini_url: str = kwargs.pop("miniUrl", None)
        self.gif100_px: str = kwargs.pop("gif100px", None)
        self.mini_poster_url: str = kwargs.pop("miniPosterUrl", None)
        self.max5_mb_gif: str = kwargs.pop("max5mbGif", None)
        self.max2_mb_gif: str = kwargs.pop("max2mbGif", None)
        self.max1_mb_gif: str = kwargs.pop("max1mbGif", None)
        self.poster_url: str = kwargs.pop("posterUrl", None)
        self.language_text: str = kwargs.pop("languageText", None)
        self.views: int = kwargs.pop("views", None)
        self.user_name: str = kwargs.pop("userName", None)
        self.description: str = kwargs.pop("description", None)
        self.sitename: str = kwargs.pop("sitename", None)
        self.has_transparency: bool = kwargs.pop("hasTransparency", None)
        self.has_audio: bool = kwargs.pop("hasAudio", None)
        self.gfy_id: str = kwargs.pop("gfyId", None)
        self.gfy_name: str = kwargs.pop("gfyName", None)
        self.width: int = kwargs.pop("width", None)
        self.height: int = kwargs.pop("height", None)
        self.frame_rate: float = kwargs.pop("frameRate", None)
        self.num_frames: int = kwargs.pop("numFrames", None)
        self.mp4_size: int = kwargs.pop("mp4Size", None)
        self.webm_size: int = kwargs.pop("webmSize", None)
        self.create_date: datetime = datetime.fromtimestamp(
            kwargs.pop("createDate", None)
        )
        self.source: int = kwargs.pop("source", None)
        self.gfy_slug: str = kwargs.pop("gfySlug", None)
        self.md5: str = kwargs.pop("md5", None)
        self.rating: typing.Any = kwargs.pop("rating", None)
        self.avg_color: str = kwargs.pop("avgColor", None)
        self.user_display_name: str = kwargs.pop("userDisplayName", None)
        self.user_profile_image_url: str = kwargs.pop("userProfileImageUrl", None)

    @staticmethod
    def from_dict(http, source):
        return Gfy(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [Gfy.from_dict(http, gfy) for gfy in source]

    def set_title(self, new_title):
        payload = {"value": new_title}

        return self._http.request(
            Route("PUT", "/me/gfycats/{id}/title", id=self["gfyId"]),
            data=json.dumps(payload),
        )

    def delete_title(self):
        return self._http.request(
            Route("DELETE", "/me/gfycats/{id}/title", id=self["gfyId"])
        )

    def delete(self):
        return self._http.request(Route("DELETE", "/me/gfycats/{id}", id=self["gfyId"]))
