"""
The script is part of the TRON (ToRainOrNot) weather widget.

Scraps weather data for locations configured in config.locations_to_cache
and sinoptik.location_ids (popular Bulgarian weather website) and
stores the data in local json files. These files are
consumed by mobile and web client.

Should be executed daily by cron job at any time after 00:01.
"""
import os

import requests
from lxml import html
import datetime
from collections import OrderedDict
import json
import config
import sinoptik


for location_name in config.locations_to_cache:
    """Cache data for each location in a separate file"""

    now = datetime.datetime.now()

    # Prepare directory
    dir = os.path.join(
        config.cache_dir,
        location_name,
    )
    os.makedirs(dir, 0o744, True)

    # Use current date as filename, to prevent using stale data
    filename = os.path.join(
        dir,
        '%s.json' % now.strftime('%Y%m%d'),
    )

    # If data for today has already been downloaded, do nothing
    if os.path.isfile(filename):
        print('Data for %s on %s already exists' % (location_name, now.strftime('%d.%m.%Y')))
        continue

    # Get the location ID
    location_id = sinoptik.get_location_id_by_name(location_name)

    # Retrieve HTML of hourly web page for that location
    url = sinoptik.hourly_url % location_id
    headers = {'User-Agent': config.mobile_user_agent}
    page = requests.get(url, headers=headers).text
    doc = html.fromstring(page)

    # Parse HTML and extract the weather data we need
    temp = doc.xpath('.//span[contains(@class, \'max-temp\')]/text()')
    rain_probability = doc.xpath('.//p[starts-with(text(),"Вероятност за валежи:")]/b/text()')
    rain_intensity = doc.xpath('.//p[starts-with(text(),"Количество валежи:")]/b/text()')

    # Group data by hour
    hour = int(now.strftime("%H"))
    hours = [str((hour + i) % 24) + ':00' for i in range(24)]
    rain = zip(temp, rain_probability, rain_intensity)
    data = OrderedDict(zip(hours, rain))

    # Write data as json file
    with open(filename, 'w+') as f:
        json.dump(data, f)
        print('Cached data for %s on %s to file %s' % (location_name, now.strftime('%d.%m.%Y'), filename))
