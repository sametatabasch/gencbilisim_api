#! /usr/bin/python3.9

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/sametatabasch/PycharmProjects/webAPI')
from webAPI import app as application
