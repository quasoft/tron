import requests
from lxml import html
import config


def get_html(url):
    """
    Download the HTML of a specific URL and returns a document object.
    :param url: URL to web page
    :return: Document object
    """
    headers = {'User-Agent': config.mobile_user_agent}
    page = requests.get(url, headers=headers).text
    return html.fromstring(page)
