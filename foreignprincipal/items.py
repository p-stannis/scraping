# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ForeignprincipalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    exhibit_urls = scrapy.Field(default=[])
    foreign_principal = scrapy.Field()
    foreign_principal_reg_date = scrapy.Field(serializer=str)
    address = scrapy.Field()
    state = scrapy.Field(default=None)
    registrant = scrapy.Field()
    reg_num = scrapy.Field()
    date = scrapy.Field(serializer=str)
    country = scrapy.Field()
