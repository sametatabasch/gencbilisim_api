#! /usr/bin/python3.9

import logging
import sys
import os

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, os.path.dirname(__file__) + '/gencbilisim_api')
from gencbilisim_api import app as application
