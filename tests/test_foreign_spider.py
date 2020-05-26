from __future__ import unicode_literals

import unittest
from unittest.mock import MagicMock

from tests import MockResponse

from foreignprincipal.spiders.foreign_spider import ForeignPrincipalSpider


class TestForeignPrincipalSpider(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.spider = ForeignPrincipalSpider()

    def test__get_request_parameters(self):
        ajax_identifier = 'AJAX_IDENTIFIER'
        p_salt = 'P_SALT'
        response = MockResponse()

        self.assertDictEqual(
            {
                'p_request': 'PLUGIN=AJAX_IDENTIFIER',
                'p_instance': 'mocked',
                'p_flow_id': 'mocked',
                'p_flow_step_id': 'mocked',
                'p_widget_name': 'worksheet',
                'x01': 'mocked',
                'x02': 'mocked',
                'p_json': '{"pageItems":null,"salt":"P_SALT"}'
            },
            self.spider._get_request_parameters(response, ajax_identifier, p_salt)
        )

    def test__get_request_headers(self):
        referer_url = 'REFERER_URL'
        self.assertDictEqual(
            {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'efile.fara.gov',
                'Origin': 'https://efile.fara.gov',
                'Referer': 'REFERER_URL',
            },
            self.spider._get_request_headers(referer_url)
        )

    def test__extract_str(self):
        header_id = 'COUNTRY'
        response = MockResponse()

        self.assertEqual('mocked', self.spider._extract_str(response, header_id))

    def test__get_exhibit_urls(self):
        mock_response = MagicMock()
        mock_response.meta = {'item': {}}

        mock_response.xpath.return_value = [
            MockResponse(),
            MockResponse(),
            MockResponse(),
        ]

        exhibit_urls_item = list(self.spider._get_exhibit_urls(mock_response))

        self.assertEqual(
            [{
                'exhibit_urls': [
                    'mocked',
                    'mocked',
                    'mocked',
                ]
            }],
            exhibit_urls_item
        )

    def test_get_ajax_identifier(self):
        ajax_identifier = '6ndxv5fJzUSo7bYCjWSOFM5s0LfsOVxODT-BEPh_1RYwhom-DOURYvIWhPB0ENij'
        mock_response = MockResponse()

        self.assertEqual(ajax_identifier, self.spider.get_ajax_identifier(mock_response))


if __name__ == '__main__':
    unittest.main()
