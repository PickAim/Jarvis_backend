import configparser


class LaunchConfigHolder:
    def __init__(self, config_path: str):
        config_parser = configparser.ConfigParser()
        config_parser.read(config_path)
        self.port: int = int(config_parser['server']['Port'])

        self.enabled_background: bool = self.__is_true(config_parser['background']['enabled'])
        self.enabled_dummies: bool = self.__is_true(config_parser['dummies']['enabled'])

    @staticmethod
    def __is_true(str_to_check: str) -> bool:
        return str_to_check.lower() == 'true'
