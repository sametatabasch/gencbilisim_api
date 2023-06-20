#! /usr/bin/python3

import os
import sys
import logging

logging.basicConfig(stream=sys.stderr)

# Proje ana klasörüne geçiş yapın
sys.path.insert(0, os.path.dirname(__file__) + '/gencbilisim_api')

# Sanal ortamı etkinleştirin
site_packages = os.path.dirname(__file__) + '/gencbilisim_api/venv/lib/python3.8/site-packages'
sys.path.insert(1, site_packages)
import site

site.addsitedir(site_packages)

# Uygulama örneğini alın
from gencbilisim_api import app as application
