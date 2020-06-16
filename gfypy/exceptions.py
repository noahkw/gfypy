__all__ = ('GfypyException', 'GfypyApiException', 'GfypyAuthException')


class GfypyException(Exception):
    def __init__(self, error_msg):
        self.error_msg = error_msg


class GfypyApiException(GfypyException):
    def __init__(self, error_msg, status_code):
        super().__init__(error_msg)
        self.status_code = status_code

    def __str__(self):
        return f"The Gfycat API responded with a {self.status_code}: {self.error_msg}"


class GfypyAuthException(GfypyApiException):
    def __init__(self, error_msg, status_code, code):
        super().__init__(error_msg, status_code)
        self.code = code

    def __str__(self):
        return f"The Gfycat API responded with a {self.status_code} / {self.code}: {self.error_msg}"
