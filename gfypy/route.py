from urllib.parse import quote


class Route:
    BASE = 'https://api.gfycat.com/v1'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        url = self.BASE + self.path
        if parameters:
            self.url = url.format(**{k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        else:
            self.url = url


class CustomRoute:
    def __init__(self, method, base, path=None):
        self.method = method
        self.base = base
        self.path = path
        if path is not None:
            self.url = self.base + self.path
        else:
            self.url = self.base
