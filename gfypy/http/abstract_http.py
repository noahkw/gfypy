class AbstractHttpClient:
    def request(self, route, **kwargs):
        return NotImplementedError
