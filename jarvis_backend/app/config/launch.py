import configparser


class LaunchConfigHolder:
    def __init__(self, config_path: str):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)
        self.port: int = config_parser.getint('server', 'Port')

        self.background_enabled: bool = config_parser.getboolean('background', 'enabled')
        self.dummies_enabled: bool = config_parser.getboolean('dummies', 'enabled')
