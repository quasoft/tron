import unittest
import logging
import sys

from server.providers.base import BaseWeatherProvider


class TestBaseProvider(unittest.TestCase):
    """
    Common tests for all providers
    """

    def test_find_provider_with_invalid_id(self):
        provider = BaseWeatherProvider.find_provider(provider_id="ThereIsNoSuchProvider")
        self.assertEqual(provider, None)

    def test_find_provider_with_invalid_location_name(self):
        provider = BaseWeatherProvider.find_provider(location_name="There is no such place")
        self.assertEqual(provider, None)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    unittest.main()
