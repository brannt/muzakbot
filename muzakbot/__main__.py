# type: ignore[attr-defined]
from typing import Optional

import argparse
import logging
import random
from enum import Enum

from muzakbot import __version__
from muzakbot.settings import MuzakbotSettings
from muzakbot.thebot import start_bot


def parse_args():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument(
        "--log-level",
        type=int,
        default=logging.INFO,
        help="Path to config file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.config is not None:
        settings = MuzakbotSettings.parse_file(args.config)
    else:
        settings = MuzakbotSettings(log_level=args.log_level)
    logging.basicConfig(level=settings.log_level)
    start_bot(settings=settings)


if __name__ == "__main__":
    main()
