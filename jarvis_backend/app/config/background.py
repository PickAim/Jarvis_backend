import configparser


class BackgroundConfigHolder:
    def __init__(self, config_path: str):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)

        self.cache_enabled: bool = config_parser.getboolean('cache', 'enabled')

        self.load_enabled: bool = config_parser.getboolean('load', 'enabled')
        self.load_skip: int = config_parser.getint('load', 'skip')

        self.update_enabled: bool = config_parser.getboolean('update', 'enabled')
