import configparser


class LaunchConfigHolder:
    def __init__(self, config_path: str):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)
        self.port: int = int(config_parser['server']['Port'])

        self.enabled_background: bool = config_parser['background']['enabled'].lower() == 'true'
