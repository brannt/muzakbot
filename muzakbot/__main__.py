# type: ignore[attr-defined]
import argparse
import random
from enum import Enum
from typing import Optional
import logging

from muzakbot import __version__
from muzakbot.settings import MuzakbotSettings
from muzakbot.thebot import start_bot


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('--log-level', type=int, default=logging.INFO, help='Path to config file')
    return parser.parse_args()

def main(config, log_level):
    if config is not None:
        settings = MuzakbotSettings.parse_file(config)
    else:
        settings = MuzakbotSettings(log_level=log_level)
    logging.basicConfig(level=settings.log_level)
    start_bot(settings=settings)

main(**vars(parse_args()))
