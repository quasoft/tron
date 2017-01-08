class ProviderMetaClass(type):
    """Metaclass that registers all provider classes in a common
       list and create a singleton global object for each provider
    """
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'provider_classes'):
            cls.provider_classes = []
            cls.providers = []
        else:
            cls.provider_classes.append(cls)
            cls.providers.append(cls())


class BaseWeatherProvider(metaclass=ProviderMetaClass):
    id = ""
    """Unique ID of provider. Each descendant should specify an ID."""

    def covers_location(self, location_id=None, location_name=None):
        """
        Check if the provider has weather data for the specified location.
        :param location_id: ID of location - specific for each provider
        :param location_name: Human readable name of location
        :return: True if provider has weather data for that location
        """
        raise NotImplementedError("Please, implement covers_location method")

    def download_data(self, location_id=None, location_name=None):
        """
        Download weather data for a specified location by its ID or name.
        :param location_id: ID of location - specific for each provider
        :param location_name: Human readable name of location
        :return: Dictionary with hourly weather data in the following format:
                 {"HH:mm": [temperature, precipation_chance, precipation_intensity], "HH:mm": ...}

                 Dictionary may be ordered by hour. Example:
                 OrderedDict([('18:00', ('2°', '17%', '0.0 mm')), ('19:00', ...
        """
        raise NotImplementedError("Please, implement download_data method")

    @classmethod
    def find_provider(cls, provider_id=None, location_name=None):
        """
        Determine provider class by provider ID or location name
        :param provider_id: ID of provider
        :param location_name: Human readable name of location
        :return: Provider object (global)
        """
        if provider_id:
            for provider in cls.providers:
                if provider.id == provider_id:
                    return provider

        if location_name:
            for provider in cls.providers:
                if provider.covers_location(location_name=location_name):
                    return provider

        return None

