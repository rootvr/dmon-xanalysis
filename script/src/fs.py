import yaml
import os


def read_yaml_from_file(path: str) -> dict:
    with open(path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def check_dir_exists(path: str) -> bool:
    return os.path.isdir(path)

def create_dir(path: str) -> None:
    os.mkdir(path)
