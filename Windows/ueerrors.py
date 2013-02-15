"""
UpdatEngine client Errors
"""

class UeImportError(Exception):
    """Response didn't return Import ok"""
    def __init__(self, response):
        self.value = response
    def __str__(self):
        return self.value

class UeResponseError(Exception):
    """Response isn't valid, XML return don't contain Import section"""
    def __init__(self, response):
        self.value = response
    def __str__(self):
        return self.value

class UeReadResponse(Exception):
    """Can't read XML Response (XML return isn't valid)"""
    def __init__(self, response):
        self.value = response
    def __str__(self):
        return self.value
