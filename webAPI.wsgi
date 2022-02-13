#! /usr/bin/python3.8

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/sametatabasch/PycharmProjects/webAPI')
from weAPI import app as application
