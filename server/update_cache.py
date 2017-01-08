"""
The script is part of the TRON (ToRainOrNot) weather widget.

Scraps weather data for locations configured in config.locations_to_cache
and sinoptik.location_ids (popular Bulgarian weather website) and
stores the data in local json files. These files are
consumed by mobile and web client.

Should be executed daily by cron job at any time after 00:01.
"""
import os
import datetime
import json
import config
from providers.base import BaseWeatherProvider
# Importing all weather providers that should be used,
# to give them a chance to register their classes
from providers.sinoptik import SinoptikProvider


for location in config.locations_to_cache:
    """Cache data for each location in a separate file"""

    location_name = location["location"]
    provider_id = location["provider"]

    now = datetime.datetime.now()

    # Prepare directory
    dir = os.path.join(
        config.cache_dir,
        location_name,
    )
    os.makedirs(dir, 0o755, True)

    # Use current date as filename, to prevent using stale data
    filename = os.path.join(
        dir,
        '%s.json' % now.strftime('%Y%m%d'),
    )

    # If data for today has already been downloaded, do nothing
    if os.path.isfile(filename):
        print('Data for %s on %s already exists' % (location_name, now.strftime('%d.%m.%Y')))
        continue

    # Find provider by ID or location name
    if provider_id:
        provider = BaseWeatherProvider.find_provider(provider_id=provider_id)
    else:
        provider = BaseWeatherProvider.find_provider(location_name=location_name)

    # Download data for next 24 hours
    data = provider.download_data(location_name=location_name)

    # Write data as json file
    with open(filename, 'w+') as f:
        json.dump(data, f)
        print('Cached data for %s on %s to file %s' % (location_name, now.strftime('%d.%m.%Y'), filename))
