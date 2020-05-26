from __future__ import unicode_literals

import unittest
from datetime import datetime
from unittest.mock import MagicMock

from scrapy.http import FormRequest, HtmlResponse, Request, Response
from tests import FakeResponse, MockResponse

from foreignprincipal.items import ForeignprincipalItem
from foreignprincipal.spiders.foreign_spider import ForeignPrincipalSpider


class TestForeignPrincipalSpider(unittest.TestCase):
    url = ''
    start_url = 'https://www.fara.gov/quick-search.html'
    browse_filling_url = 'https://efile.fara.gov/ords/f?p=1381:1:9305730020345:::::'
    active_foreign_principal_url = 'https://efile.fara.gov/ords/f?p=1381:130:9066584635823::NO:RP,130:P130_DATERANGE:N'
    links = None
    expected_items = None

    xhr_backend_url = 'https://efile.fara.gov/pls/apex/wwv_flow.ajax'
    fake_principal_index_page = FakeResponse('browse_fillings.html', browse_filling_url)

    def setUp(self):
        super().setUp()
        self.spider = ForeignPrincipalSpider()

    def test_parse_initial_page(self):
        with open('tests/htmlresponses/browse_fillings.html', 'r') as browse_filling_page:
            body = browse_filling_page.read().replace('\n', '')

            request = Request(url=self.start_url, callback=self.spider.parse)
            response = HtmlResponse(url=self.browse_filling_url, body=body, encoding='utf-8', request=request)

            active_foreign_principal = response.xpath('//font[text()="Active Foreign Principals"]/../../a/@href')

            assert active_foreign_principal is not None

    # def test__add_country_column(self):
    #     with open('tests/htmlresponses/active_foreign_principals.html', 'r') as browse_filling_page:
    #         body = browse_filling_page.read().replace('\n', '')

    #         request = Request(
    #             url=self.start_url, callback=self.spider._parse_initial_page)
    #         response = Response(
    #             url=self.active_foreign_principal_url,
    #             body=body.encode(), request=request)
    #         import pdb; pdb.set_trace()
    #         yield_response = list(ForeignPrincipalSpider()._add_country_column(response))


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




if __name__ == '__main__':
    unittest.main()


        # item = response.meta.get('item')
        # item['exhibit_urls'] = []
        # docs = response.xpath('//table[@class="a-IRR-table"]//tr/td[@headers="DOCLINK"]')

        # for doc_link_urls in docs:
        #     exhibit_url = doc_link_urls.xpath('./a/@href').extract_first()
        #     item['exhibit_urls'].append(exhibit_url)

        # yield item
