from args import ArgParser
from driver import Driver


def main():
    ap = ArgParser()
    dv = Driver(ap.args)
    dv.run()


if __name__ == "__main__":
    main()
