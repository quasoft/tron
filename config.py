mobile_user_agent = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
"""User agent to present our app as mobile web browser."""

desktop_user_agent = "Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0"
"""User agent to present our app as desktop web browser."""

cache_dir = 'data/'
"""path to directory where cached weather data should be stored."""

locations_to_cache = [
    "Велико Търново",
    "София",
]
"""List of locations to cache data for. The names in this list should match the names used in sinoptik list above."""
