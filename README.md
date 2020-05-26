# Scraping Active Foreign Principals
This is a Scrapy project to scrape data from the DOJ Foreign Agents Registration Act website:
```
https://www.fara.gov/quick-search.html 
```
The goal is to scrape the all Active Foreign Principals present in the site.

## Extracted data

The following sample shows actual data extracted from the Active Foreign Principals site:
```json
{
    "country": "RUSSIA",
    "foreign_principal": "Uranium One, Inc.",
    "foreign_principal_reg_date": "2019-02-18 00:00:00",
    "address": "333 Bay Street #12--",
    "state": "",
    "registrant": "Tenam Corporation",
    "reg_num": "6638",
    "date": "2019-02-18 00:00:00",
    "url": "https://efile.fara.gov/ords/f?p=1381:200:5265451153848::NO:RP,200:P200_REG_NUMBER,P200_DOC_TYPE,P200_COUNTRY:6638,Exhibit%20AB,RUSSIA",
    "exhibit_urls": [
        "https://efile.fara.gov/docs/6638-Exhibit-AB-20190517-2.pdf",
        "https://efile.fara.gov/docs/6638-Exhibit-AB-20190218-1.pdf"
    ]
}
```
## Requirements
* Python 3.8.x
* Scrapy 2.1.0

## Install requirements

    $ cd scraping
    $ pip install -r requirements.txt 

## How to run scrapy spiders

You can run the spider using:

    $ cd scraping
    $ scrapy crawl foreign

All the data that was scraped from the Active Foreign Principals will be saved in the items.json

## Run the tests

    $ cd scraping
    $ python -m unittest