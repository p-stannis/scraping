from __future__ import absolute_import
import scrapy
from foreignprincipal import items
from collections import defaultdict

class ForeignPrincipalSpider(scrapy.Spider):
    name = 'foreign'
    start_urls = [
        'https://www.fara.gov/quick-search.html'
    ]
    url_key_name = 'first_page_url'
    fara_gov_ajax_call = 'https://efile.fara.gov/ords/wwv_flow.ajax'
    ajax_identifier = ''
    p_salt = ''

    def parse(self, response):
        url = response.xpath('//iframe/@src').extract_first()
        yield scrapy.Request(response.urljoin(url), self._parse_initial_page)

    def _parse_initial_page(self, response):
        url = scrapy.Selector(response).xpath("//font[text()='Active Foreign Principals']/../../a/@href").extract_first()
        yield scrapy.Request(response.urljoin(url), self._add_country_column)

    def _add_country_column(self, response):
        js_code = response.xpath('//script').re(r'"ajaxIdentifier":\s*(.+)')[1]
        self.ajax_identifier = str(js_code).replace('});})();','').replace('"','')
        self.p_salt = response.xpath('//input[@id="pSalt"]/@value').extract_first()

        url = response.request.url
        if url == self.fara_gov_ajax_call:
            url = response.meta.get(self.url_key_name)

        meta = {}

        header_vars = self._get_request_headers(url)

        params = self._get_request_parameters(response, self.ajax_identifier, self.p_salt)
        params['p_widget_num_return'] = '1000'
        params['p_widget_mod'] = 'ACTION'
        params['p_widget_action'] = 'BREAK'
        params['x03'] = 'COUNTRY_NAME'

        meta[self.url_key_name] = url
        meta['params'] = params

        yield scrapy.FormRequest(self.fara_gov_ajax_call,
                                 method="POST",
                                 headers=header_vars,
                                 formdata=params,
                                 callback=self._format_show_all_rows,
                                 meta = meta)


    def _format_show_all_rows(self, response):

        url = response.request.url
        if url == self.fara_gov_ajax_call:
            url = response.meta.get(self.url_key_name)

        header_vars = self._get_request_headers(url)

        params = response.meta['params']
        params['p_widget_num_return'] = '1000'
        params['p_widget_mod'] = 'PULL'
        params['p_widget_action'] = ''

        yield scrapy.FormRequest(self.fara_gov_ajax_call,
                                 method="POST",
                                 headers=header_vars,
                                 formdata=params,
                                 callback=self._get_table_info)

    def _get_table_info(self, response):
        table = response.xpath('//table[@class="a-IRR-table"]//tr')

        for row in table:
            header_row = row.xpath('./th[@class="a-IRR-header u-tL"]').extract_first()
            if header_row is not None:
                continue

            item = items.ForeignprincipalItem()
            item['country'] = self._extract_str(row, 'COUNTRY_NAME')
            item['foreign_principal'] = self._extract_str(row, 'FP_NAME')
            item['foreign_principal_reg_date'] = self._extract_str(row, 'FP_REG_DATE')
            item['address'] = self._extract_str(row, 'ADDRESS_1')
            item['state'] = self._extract_str(row, 'STATE')
            item['registrant'] = self._extract_str(row, 'REGISTRANT_NAME')
            item['reg_num'] = self._extract_str(row, 'REG_NUMBER')
            item['date'] = self._extract_str(row, 'REG_DATE')

            item_url = response.urljoin(row.xpath('./td[contains(@headers, "LINK")]/a/@href').extract_first())
            item['url'] = item_url

            yield scrapy.Request(item_url, callback=self._get_exhibit_urls, meta={'item': item}, dont_filter=True)

    def _get_exhibit_urls(self, response):
        item = response.meta.get('item')
        item['exhibit_urls'] = []
        docs = response.xpath('//table[@class="a-IRR-table"]//tr/td[@headers="DOCLINK"]')

        for doc_link_urls in docs:
            exhibit_url = doc_link_urls.xpath('./a/@href').extract_first()
            item['exhibit_urls'].append(exhibit_url)

        yield item

    @staticmethod
    def _patch_dictionary(source, destination):
        data = destination.copy()
        data.update(source)
        return data

    @staticmethod
    def _get_request_headers(referer_url):
        return {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'efile.fara.gov',
            'Origin': 'https://efile.fara.gov',
            'Referer': referer_url,
        }

    @staticmethod
    def _get_request_parameters(response, ajax_identifier, p_salt):
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
    def _extract_str(row, header_id):
        item = row.xpath('./td[contains(@headers, "%s")]/text()' % header_id).extract_first()

        if item is None:
            return ''

        item = item.replace('\u00a0\u00a0', '')
        item = item.strip()

        return item or None