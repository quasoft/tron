import unittest
import logging
import sys
from server import utils


class TestUtils(unittest.TestCase):
    """
    Tests for utils
    """

    @unittest.skip("Skipping test, requiring Internet access")
    def test_get_html(self):
        log = logging.getLogger("TestUtils.test_get_html")

        url = "http://www.google.com"
        html = utils.get_html(url)
        body = html.xpath('.//body')
        self.assertTrue(len(body) >= 1 and body[0].tag == "body")


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
