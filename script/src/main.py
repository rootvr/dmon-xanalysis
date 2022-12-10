import os
import sys

import meta
from fs import read_yaml_from_file, check_dir_exists, create_dir
from args import ArgParser


def create_env(data: dict) -> None:
    app = data[meta.APP_KEY]
    data_dir = data[meta.DATA_DIR_KEY]
    durations = data[meta.DURATIONS_KEY]
    jupyter_dir = data[meta.JUPYTER_DIR_KEY]

    if(not check_dir_exists(os.path.join(meta.BASE_DIR))):
        create_dir(meta.BASE_DIR)

    if check_dir_exists(os.path.join(meta.BASE_DIR, app)):
        print(meta.DATA_DIR_EXISTS_ERROR)
        sys.exit(1)
        
    create_dir(os.path.join(meta.BASE_DIR, app))
    create_dir(os.path.join(meta.BASE_DIR, app, data_dir))
    create_dir(os.path.join(meta.BASE_DIR, app, jupyter_dir))

    for d in durations:
        create_dir(os.path.join(meta.BASE_DIR, app, data_dir, d))


def main():
    arg_parser = ArgParser()
    data = read_yaml_from_file(arg_parser.args.config_file)
    create_env(data)


if __name__ == '__main__':
    main()
