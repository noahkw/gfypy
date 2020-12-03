class AbstractHttpClient:
    def close(self):
        raise NotImplementedError

    def request(self, route, **kwargs):
        raise NotImplementedError
