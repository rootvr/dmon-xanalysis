import argparse


class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="workspace creator")
        self.parser.add_argument(
            "-c",
            "--config-file",
            type=str,
            dest="config_file",
            metavar="CONFIG_FILE",
            required=True,
            help="path to YAML configuration file",
        )
        self.args = self.parser.parse_args()
