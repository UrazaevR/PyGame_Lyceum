import configparser
import os


def start_config() -> None:
    """Функция для проверки наличия файла с настройками или в противном случае его создания"""
    if not os.path.exists('Settings.ini') or os.path.getsize('Settings.ini') == 0:
        x = open('Settings.ini', 'w')
        x.write('\n'.join(['[Setting]', 'music_volume = 50', 'sound_volume = 50', 'best_score = 0']))
        x.close()


def read_set(name: str) -> str:
    """Функция для чтения конфигураций из ini-файла
    На вход получает имя конфигурации, а возвращает ее значение в строковом формате"""
    config = configparser.ConfigParser()
    config.read('Settings.ini')
    return config["Setting"][name]


def save_conf(name: str, value) -> None:
    """Функция для сохранения нового значения value конфигурации name в файл"""
    config = configparser.ConfigParser()
    config.read('Settings.ini')
    config["Setting"][name] = str(value)
    with open("settings.ini", "w") as f:
        config.write(f)