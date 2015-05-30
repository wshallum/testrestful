import unittest
import os
import urllib


class BaseBackendTest(unittest.TestCase):
    # append message to normal message so we have info on what the unequal
    # values are
    longMessage = True

    def __init__(self, method_name):
        super(BaseBackendTest, self).__init__(method_name)
        self.backend_base_url = os.getenv('PHONEBOOK_BACKEND_BASE_URL')
        if self.backend_base_url is None:
            raise KeyError("No PHONEBOOK_BACKEND_BASE_URL in os environment")

    def url(self, path, params=None):
        if params is None:
            params = dict()
        result = self.backend_base_url + path
        if len(params) > 0:
            result = result + '?' + urllib.urlencode(params)
        return result

    def assertResponseCodeAndContentType(
            self, response, code, content_type, message=None):
        self.assertEqual(response.status_code, code, message)
        self.assertEqual(
            response.headers['content-type'], content_type, message)
