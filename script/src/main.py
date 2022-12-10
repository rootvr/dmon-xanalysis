from args import ArgParser
from driver import Driver


def main():
    arg_parser = ArgParser()
    Driver(arg_parser.args).run()


if __name__ == "__main__":
    main()
