import unittest
import logging
import sys

from providers.base import BaseWeatherProvider
from providers.sinoptik import SinoptikProvider


class TestSinoptikProvider(unittest.TestCase):
    """
    Common tests for all providers
    """

    def test_find_provider_with_id(self):
        provider = BaseWeatherProvider.find_provider(provider_id="sinoptik")
        self.assertEqual(provider.__class__.__name__, 'SinoptikProvider')

    def test_find_provider_with_location_name(self):
        provider = BaseWeatherProvider.find_provider(location_name="Велико Търново")
        self.assertEqual(provider.__class__.__name__, 'SinoptikProvider')

    @unittest.skip("Skipping test, requiring access to sinoptik website")
    def test_download_data(self):
        log = logging.getLogger("TestSinoptikProvider.test_download_data")

        sinoptik = SinoptikProvider()
        data = sinoptik.download_data(location_name="Велико Търново")
        for item in list(data.items()):
            hour = item[0]
            values = item[1]
            log.info("Hour: %s", hour)
            log.info("Values: %s, %d", values, len(values))
            self.assertTrue(3 < len(hour) < 6 and ":" in hour)
            self.assertTrue(len(values) == 3)

    @unittest.skip("Skipping test, requiring access to sinoptik website")
    def test_scrap_locations(self):
        log = logging.getLogger("TestSinoptikProvider.test_download_data")

        sinoptik = SinoptikProvider()
        sinoptik.locations = []
        locations_str = sinoptik.download_locations()
        self.assertTrue(locations_str)
        self.assertTrue(len(sinoptik.locations) > 100)

        velikoTarnovo = next((c for c in sinoptik.locations if c['name'] == "Велико Търново"), None)
        self.assertTrue(velikoTarnovo["name"] == "Велико Търново" and velikoTarnovo["id"] == "veliko-turnovo-bulgaria-100725993")

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
