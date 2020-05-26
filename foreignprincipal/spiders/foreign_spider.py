from __future__ import absolute_import

import scrapy

from datetime import datetime
import re
from foreignprincipal import items


class ForeignPrincipalSpider(scrapy.Spider):
    name = 'foreign'
    start_urls = [
        'https://www.fara.gov/quick-search.html'
    ]
    url_key_active_foreign_principal = 'active_foreign_principals'
    fara_gov_ajax_call = 'https://efile.fara.gov/ords/wwv_flow.ajax'
    ajax_identifier = ''
    p_salt = ''

    country_page_params = {
        'p_widget_num_return': '1000',
        'p_widget_mod': 'ACTION',
        'p_widget_action': 'BREAK',
        'x03': 'COUNTRY_NAME',
    }

    show_all_rows_params = {
        'p_widget_num_return': '1000',
        'p_widget_mod':  'PULL',
        'p_widget_action':  ''
    }

    def parse(self, response):
        yield scrapy.Request(response.url, self._parse_initial_page)

    def _parse_initial_page(self, response):
        '''
        Find the Active Foreign Principals @href

        :param response: scrapy response
        :return: scrapy request
        '''
        url = response.xpath("//font[text()='Active Foreign Principals']/../../a/@href").extract_first()

        if url is None:
            raise scrapy.exceptions.CloseSpider('Active Foreign Principals was not found.')

        yield scrapy.Request(response.urljoin(url), self._add_country_column)

    def get_ajax_identifier(self, response):
        '''
            In order to send a POST request to the https://efile.fara.gov/ords/wwv_flow.ajax url,
            the body needs a p_request value. This value is an ajax identifier.
            By analyzing the page source, there are two ajax identifiers. We need the second one
            in order to get a successful from fara gov.
        '''
        js_code = response.xpath('//script').re(r'"ajaxIdentifier":\s*(.+)')[1]

        return re.sub('[});("]+', '', str(js_code))

    def _add_country_column(self, response):
        '''
        Remove the initial Country/Location filter

        :param response: scrapy Response
        :return: scrapy FormRequest
        '''
        self.ajax_identifier = self.get_ajax_identifier(response)
        self.p_salt = response.xpath('//input[@id="pSalt"]/@value').extract_first()

        url = response.request.url
        if url == self.fara_gov_ajax_call:
            url = response.meta.get(self.url_key_active_foreign_principal)

        meta = {}

        header_vars = self._get_request_headers(url)

        params = self._get_request_parameters(response, self.ajax_identifier, self.p_salt)
        params.update(self.country_page_params)

        meta[self.url_key_active_foreign_principal] = url
        meta['params'] = params

        yield scrapy.FormRequest(self.fara_gov_ajax_call,
                                 method="POST",
                                 headers=header_vars,
                                 formdata=params,
                                 callback=self._format_show_all_rows,
                                 meta=meta)


    def _format_show_all_rows(self, response):
        '''
        Format the site to show all active foreign principals in one
        single page

        :param response: scrapy Response
        :return: scrapy FormRequest
        '''
        url = response.request.url
        if url == self.fara_gov_ajax_call:
            url = response.meta.get(self.url_key_active_foreign_principal)

        header_vars = self._get_request_headers(url)

        params = response.meta['params']
        params.update(self.show_all_rows_params)

        yield scrapy.FormRequest(self.fara_gov_ajax_call,
                                 method="POST",
                                 headers=header_vars,
                                 formdata=params,
                                 callback=self._get_table_info)

    def _get_table_info(self, response):
        '''
        Scraping the active foreign principal's information.


        :param response: scrapy response
        :return: scrapy Request
        '''
        table = response.xpath('//table[@class="a-IRR-table"]//tr')

        if not table:
            raise scrapy.exceptions.CloseSpider('Could not find table with data')

        for row in table:
            header_row = row.xpath('./th[@class="a-IRR-header u-tL"]').extract_first()
            if header_row is not None:
                continue

            item = items.ForeignprincipalItem()
            item['country'] = self._extract_str(row, 'COUNTRY_NAME')
            item['foreign_principal'] = self._extract_str(row, 'FP_NAME')
            item['foreign_principal_reg_date'] = datetime.strptime(self._extract_str(row, 'FP_REG_DATE'), '%m/%d/%Y')
            item['address'] = self._extract_str(row, 'ADDRESS_1')
            item['state'] = self._extract_str(row, 'STATE')
            item['registrant'] = self._extract_str(row, 'REGISTRANT_NAME')
            item['reg_num'] = self._extract_str(row, 'REG_NUMBER')
            item['date'] = datetime.strptime(self._extract_str(row, 'REG_DATE'), '%m/%d/%Y')

            item_url = response.urljoin(row.xpath('./td[contains(@headers, "LINK")]/a/@href').extract_first())
            item['url'] = item_url

            yield scrapy.Request(item_url, callback=self._get_exhibit_urls, meta={'item': item}, dont_filter=True)

    def _get_exhibit_urls(self, response):
        '''
        After a scrapy Request is made, get the exhibit_urls from the documents page of each
        active foreign principal

        :param response: scrapy response
        :return: ForeignprincipalItem
        '''
        item = response.meta.get('item')
        item['exhibit_urls'] = []
        docs = response.xpath('//table[@class="a-IRR-table"]//tr/td[@headers="DOCLINK"]')

        for doc_link_urls in docs:
            exhibit_url = doc_link_urls.xpath('./a/@href').extract_first()
            item['exhibit_urls'].append(exhibit_url)

        yield item

    @staticmethod
    def _get_request_headers(referer_url: str) -> dict:
        return {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'efile.fara.gov',
            'Origin': 'https://efile.fara.gov',
            'Referer': referer_url,
        }

    @staticmethod
    def _get_request_parameters(response: any, ajax_identifier: str, p_salt: str) -> dict:
        return {
            'p_request': 'PLUGIN=' + ajax_identifier,
            'p_instance': response.xpath('//input[@id="pInstance"]/@value').extract_first(),
            'p_flow_id': response.xpath('//input[@id="pFlowId"]/@value').extract_first(),
            'p_flow_step_id': response.xpath('//input[@id="pFlowStepId"]/@value').extract_first(),
            'p_widget_name': 'worksheet',
            'x01': response.xpath('//input[contains(@id,"_worksheet_id")]/@value').extract_first(),
            'x02': response.xpath('//input[contains(@id,"_report_id")]/@value').extract_first(),
            'p_json': '{"pageItems":null,"salt":"' + p_salt + '"}'
        }

    @staticmethod
    def _extract_str(row, header_id: str) -> str:
        item = row.xpath(f'./td[contains(@headers, "{header_id}")]/text()').extract_first()

        if item is None:
            return ''

        item = item.replace('\u00a0', '')
        item = item.strip()

        return item
