from __future__ import unicode_literals
import os
import unittest
from unittest import TestCase

from scrapy.http import HtmlResponse, Request, FormRequest
from datetime import datetime

from foreignprincipal.spiders.foreign_spider import ForeignPrincipalSpider
from foreignprincipal.items import ForeignprincipalItem


class FakeResponse(object):
    status = 200
    body = bytes()

    def __init__(self, file_name, url):
        self.url = url

        base_dir = os.path.dirname(os.path.realpath(__file__))

        f = open(os.path.join(base_dir, 'htmlresponses', file_name))
        self.body = bytes(f.read(), encoding='utf8')
        f.close()

        self.text = str(self.body)


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
        super(TestForeignPrincipalSpider, self).setUp()
        self.spider = ForeignPrincipalSpider()

    def test_parse_initial_page(self):
        with open('htmlresponses/browse_fillings.html', 'r') as browse_filling_page:
            body = browse_filling_page.read().replace('\n', '')

            request = Request(url=self.start_url, callback=self.spider.parse)
            response = HtmlResponse(url=self.browse_filling_url, body=body, encoding='utf-8', request=request)

            active_foreign_principal = response.xpath('//font[text()="Active Foreign Principals"]/../../a/@href')

            assert active_foreign_principal is not None

    def test__add_country_column(self):
        with open('htmlresponses/active_foreign_principals.html', 'r') as browse_filling_page:
            body = browse_filling_page.read().replace('\n', '')

            request = Request(url=self.start_url, callback=self.spider._parse_initial_page)
            response = HtmlResponse(url=self.active_foreign_principal_url, body=body, encoding='utf-8', request=request)

            js_code = response.xpath('//script').re(r'"ajaxIdentifier":\s*(.+)')[1]
            self.ajax_identifier = str(js_code).replace('});})();', '').replace('"', '')
            self.p_salt = response.xpath('//input[@id="pSalt"]/@value').extract_first()
            print('')

if __name__ == '__main__':
    unittest.main()


