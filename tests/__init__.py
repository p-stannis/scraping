import os


class FakeResponse:
    status = 200
    body = bytes()

    def __init__(self, file_name, url):
        self.url = url

        base_dir = os.path.dirname(os.path.realpath(__file__))
        f = open(os.path.join(base_dir, 'htmlresponses', file_name))
        self.body = bytes(f.read(), encoding='utf8')
        f.close()

        self.text = str(self.body)


class MockXpath:

    def extract_first(self):
        return 'mocked'

class MockResponse:

    def xpath(self, path):
        return MockXpath()
