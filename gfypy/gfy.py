import json
from datetime import datetime

from .route import Route

from dataclasses import dataclass
from typing import List, Any, Set, Optional


@dataclass
class ContentUrl:
    url: str
    size: int
    height: int
    width: int

    def __init__(self, **kwargs):
        self.url = kwargs.pop('url', None)
        self.size = kwargs.pop('size', None)
        self.height = kwargs.pop('height', None)
        self.width = kwargs.pop('width', None)


@dataclass
class UserData:
    name: str
    profile_image_url: str
    url: str
    username: str
    followers: int
    subscription: int
    following: int
    profile_url: str
    views: int
    verified: bool

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)
        self.profile_image_url = kwargs.pop('profileImageUrl', None)
        self.url = kwargs.pop('url', None)
        self.username = kwargs.pop('username', None)
        self.followers = kwargs.pop('followers', None)
        self.subscription = kwargs.pop('subscription', None)
        self.following = kwargs.pop('following', None)
        self.profile_url = kwargs.pop('profileUrl', None)
        self.views = kwargs.pop('views', None)
        self.verified = kwargs.pop('verified', None)


@dataclass
class ContentUrls:
    max2_mb_gif: ContentUrl
    webp: ContentUrl
    max1_mb_gif: ContentUrl
    _100_px_gif: ContentUrl
    mobile_poster: ContentUrl
    mp4: ContentUrl
    webm: ContentUrl
    max5_mb_gif: ContentUrl
    large_gif: ContentUrl
    mobile: ContentUrl

    def __init__(self, **kwargs):
        self.max2_mb_gif = ContentUrl(**kwargs.pop('max2mbGif')) if 'max2mbGif' in kwargs else None
        self.webp = ContentUrl(**kwargs.pop('webp')) if 'webp' in kwargs else None
        self.max1_mb_gif = ContentUrl(**kwargs.pop('max1mbGif')) if 'max1mbGif' in kwargs else None
        self._100_px_gif = ContentUrl(**kwargs.pop('100pxGif')) if '100pxGif' in kwargs else None
        self.mobile_poster = ContentUrl(**kwargs.pop('mobilePoster')) if 'mobilePoster' in kwargs else None
        self.mp4 = ContentUrl(**kwargs.pop('mp4')) if 'mp4' in kwargs else None
        self.webm = ContentUrl(**kwargs.pop('webm')) if 'webm' in kwargs else None
        self.max5_mb_gif = ContentUrl(**kwargs.pop('max5mbGif')) if 'max5mbGif' in kwargs else None
        self.large_gif = ContentUrl(**kwargs.pop('largeGif')) if 'largeGif' in kwargs else None
        self.mobile = ContentUrl(**kwargs.pop('mobile')) if 'mobile' in kwargs else None


@dataclass
class Gfy(dict):
    tags: Set[str]
    language_categories: List[Any]
    domain_whitelist: List[Any]
    geo_whitelist: List[Any]
    published: int
    nsfw: str
    gatekeeper: int
    mp4_url: str
    gif_url: str
    webm_url: str
    webp_url: str
    mobile_url: str
    mobile_poster_url: str
    extra_lemmas: str
    thumb100_poster_url: str
    mini_url: str
    gif100_px: str
    mini_poster_url: str
    max5_mb_gif: str
    title: str
    max2_mb_gif: str
    max1_mb_gif: str
    poster_url: str
    language_text: str
    views: int
    user_name: str
    description: str
    sitename: str
    has_transparency: bool
    has_audio: bool
    likes: int
    dislikes: int
    gfy_number: int
    user_display_name: str
    user_profile_image_url: str
    gfy_id: str
    gfy_name: str
    avg_color: str
    width: int
    height: int
    frame_rate: float
    num_frames: int
    mp4_size: int
    webm_size: int
    create_date: datetime
    source: int
    content_urls: Optional[ContentUrls]
    user_data: Optional[UserData]

    def __init__(self, http, **kwargs):
        super().__init__(kwargs)
        self._http = http
        self._source = kwargs

        self.content_urls = ContentUrls(**kwargs.pop('content_urls', {}))
        self.user_data = UserData(**kwargs.pop('userData', {}))

        # explicit cast to int required because the API sometimes returns a str
        self.likes = int(kwargs.pop('likes', 0))
        self.dislikes = int(kwargs.pop('dislikes', 0))
        self.gfy_number = int(kwargs.pop('gfyNumber', 0))

        self.title = kwargs.pop('title', None)
        self.tags = set(kwargs.pop('tags', None))
        self.language_categories = kwargs.pop('languageCategories', [])
        self.domain_whitelist = kwargs.pop('domainWhitelist', [])
        self.geo_whitelist = kwargs.pop('geoWhitelist', [])
        self.published = kwargs.pop('published', None)
        self.nsfw = kwargs.pop('nsfw', None)
        self.gatekeeper = kwargs.pop('gatekeeper', None)
        self.mp4_url = kwargs.pop('mp4Url', None)
        self.gif_url = kwargs.pop('gifUrl', None)
        self.webm_url = kwargs.pop('webmUrl', None)
        self.webp_url = kwargs.pop('webpUrl', None)
        self.mobile_url = kwargs.pop('mobileUrl', None)
        self.mobile_poster_url = kwargs.pop('mobilePosterUrl', None)
        self.extra_lemmas = kwargs.pop('extraLemmas', None)
        self.thumb100_poster_url = kwargs.pop('thumb100PosterUrl', None)
        self.mini_url = kwargs.pop('miniUrl', None)
        self.gif100_px = kwargs.pop('gif100px', None)
        self.mini_poster_url = kwargs.pop('miniPosterUrl', None)
        self.max5_mb_gif = kwargs.pop('max5mbGif', None)
        self.max2_mb_gif = kwargs.pop('max2mbGif', None)
        self.max1_mb_gif = kwargs.pop('max1mbGif', None)
        self.poster_url = kwargs.pop('posterUrl', None)
        self.language_text = kwargs.pop('languageText', None)
        self.views = kwargs.pop('views', None)
        self.user_name = kwargs.pop('userName', None)
        self.description = kwargs.pop('description', None)
        self.sitename = kwargs.pop('sitename', None)
        self.has_transparency = kwargs.pop('hasTransparency', None)
        self.has_audio = kwargs.pop('hasAudio', None)
        self.gfy_id = kwargs.pop('gfyId', None)
        self.gfy_name = kwargs.pop('gfyName', None)
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        self.frame_rate = kwargs.pop('frameRate', None)
        self.num_frames = kwargs.pop('numFrames', None)
        self.mp4_size = kwargs.pop('mp4Size', None)
        self.webm_size = kwargs.pop('webmSize', None)
        self.create_date = datetime.fromtimestamp(kwargs.pop('createDate', None))
        self.source = kwargs.pop('source', None)
        self.gfy_slug = kwargs.pop('gfySlug', None)
        self.md5 = kwargs.pop('md5', None)
        self.rating = kwargs.pop('rating', None)
        self.avg_color = kwargs.pop('avgColor', None)
        self.user_display_name = kwargs.pop('userDisplayName', None)
        self.user_profile_image_url = kwargs.pop('userProfileImageUrl', None)

    @staticmethod
    def from_dict(http, source):
        return Gfy(http, **source)

    @staticmethod
    def from_dict_list(http, source):
        return [Gfy.from_dict(http, gfy) for gfy in source]

    def set_title(self, new_title):
        payload = {
            'value': new_title
        }

        return self._http.request(Route('PUT', '/me/gfycats/{id}/title', id=self['gfyId']), data=json.dumps(payload))

    def delete_title(self):
        return self._http.request(Route('DELETE', '/me/gfycats/{id}/title', id=self['gfyId']))

    def delete(self):
        return self._http.request(Route('DELETE', '/me/gfycats/{id}', id=self['gfyId']))
