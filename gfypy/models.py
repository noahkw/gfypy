class Gfy:
    def __init__(self, **kwargs):
        self.tags = kwargs['tags']
        self.languageCategories = kwargs['languageCategories']
        self.domainWhitelist = kwargs['domainWhitelist']
        self.geoWhitelist = kwargs['geoWhitelist']
        self.published = kwargs['published']
        self.nsfw = kwargs['nsfw']
        self.gatekeeper = kwargs['gatekeeper']
        self.mp4Url = kwargs['mp4Url']
        self.gifUrl = kwargs['gifUrl']
        self.webmUrl = kwargs['webmUrl']
        self.webpUrl = kwargs['webpUrl']
        self.mobileUrl = kwargs['mobileUrl']
        self.mobilePosterUrl = kwargs['mobilePosterUrl']
        self.thumb100PosterUrl = kwargs['thumb100PosterUrl']
        self.miniUrl = kwargs['miniUrl']
        self.gif100px = kwargs['gif100px']
        self.miniPosterUrl = kwargs['miniPosterUrl']
        self.max5mbGif = kwargs['max5mbGif']
        self.max2mbGif = kwargs['max2mbGif']
        self.max1mbGif = kwargs['max1mbGif']
        self.posterUrl = kwargs['posterUrl']
        self.title = kwargs['title']
        self.views = kwargs['views']
        self.description = kwargs['description']
        self.hasTransparency = kwargs['hasTransparency']
        self.hasAudio = kwargs['hasAudio']
        self.likes = kwargs['likes']
        self.dislikes = kwargs['dislikes']
        self.gfyNumber = kwargs['gfyNumber']
        self.gfyId = kwargs['gfyId']
        self.gfyName = kwargs['gfyName']
        self.avgColor = kwargs['avgColor']
        # Gfycat does not always return the gfySlug property
        self.gfySlug = kwargs['gfySlug'] if 'gfySlug' in kwargs else None
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.frameRate = kwargs['frameRate']
        self.numFrames = kwargs['numFrames']
        self.mp4Size = kwargs['mp4Size']
        self.webmSize = kwargs['webmSize']
        self.createDate = kwargs['createDate']
        # Gfycat does not always return the md5 property
        self.md5 = kwargs['md5'] if 'md5' in kwargs else None
        self.source = kwargs['source']

    def __getitem__(self, attr):
        """Makes Gfy objects behave like a dict"""
        return getattr(self, attr)

    @staticmethod
    def from_dict(source):
        return Gfy(**source)

    @staticmethod
    def from_dict_list(source):
        return [Gfy.from_dict(gfy) for gfy in source]

