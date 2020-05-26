class MockXpath:

    def extract_first(self):
        return 'mocked'

    def re(self,path):
       return ['"QD4JGKwGDHq5RIrCfu7-wLKaMlCduB7PQE1dIe0sdvHV4Gm3xazPKs0kw6XmM1Nk"});})();', '"6ndxv5fJzUSo7bYCjWSOFM5s0LfsOVxODT-BEPh_1RYwhom-DOURYvIWhPB0ENij"});})();']

class MockResponse:

    def xpath(self, path):
        return MockXpath()