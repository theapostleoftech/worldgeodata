import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scripts.seed_geo_data import main as seed_main


def main():
    parser = argparse.ArgumentParser(description="Management command runner")
    parser.add_argument("command", choices=["seed_geo_data"])
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    if args.command == "seed_geo_data":
        if args.reset:
            sys.argv = ["seed_geo_data.py", "--reset"]
        else:
            sys.argv = ["seed_geo_data.py"]
        seed_main()


if __name__ == "__main__":
    main()
