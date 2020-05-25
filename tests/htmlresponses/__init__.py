import os

from scrapy.http import HtmlResponse, TextResponse, Request

def fake_response_from_file(file_name, callback,url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'https://www.fara.gov/quick-search.html'

    request = Request(url=url, callback = callback)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    f = open(file_path, 'r')
    file_content = bytes(f.read(), encoding='utf8')

    response = HtmlResponse(url=url, request=request,body=file_content, encoding='utf-8')
    return response
