import os
import sys
import argparse
import pathlib


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parserInfo(_, msg):
    print(msg)


def parserPanic(parser, msg):
    eprint(msg)
    parser.print_help()
    sys.exit(1)


def checkDirExistsAndResolve():
    class CheckDirExistsAndResolve(argparse.Action):
        def __call__(self, parser, args, root_dir, _) -> None:
            if os.path.isdir(root_dir):
                parserInfo(parser, f"INFO: dir `{root_dir}` already exists")
            os.makedirs(os.path.abspath(root_dir), exist_ok=True)
            setattr(args, self.dest, pathlib.Path(root_dir).resolve(strict=True))

    return CheckDirExistsAndResolve


def checkFileExistsAndResolveOrError():
    class CheckFileExistsAndResolveOrError(argparse.Action):
        def __call__(self, parser, args, yaml_file, _) -> None:
            if not os.path.isfile(yaml_file):
                parserPanic(parser, f"ERROR: file `{yaml_file}` does not exists")
            setattr(args, self.dest, pathlib.Path(yaml_file).resolve(strict=True))

    return CheckFileExistsAndResolveOrError


class ArgParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="dmon-xdriver workflow runner"
        )

        self.parser.add_argument(
            "-w",
            "--workflow-yaml-file",
            type=str,
            dest="workflow_file",
            metavar="FILE_NAME",
            required=True,
            help="/path/to/workflow/file.yml",
            action=checkFileExistsAndResolveOrError(),
        )
        self.parser.add_argument(
            "-p",
            "--tests-root-dir",
            type=str,
            dest="root_dir",
            metavar="DIR_NAME",
            required=True,
            help="/path/to/tests/root/dir",
            action=checkDirExistsAndResolve(),
        )

        self.args = self.parser.parse_args()
