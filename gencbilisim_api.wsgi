#! /usr/bin/python3
import sys
import logging
import os

logging.basicConfig(stream=sys.stderr)

app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Proje ana klasörüne geçiş yapın
sys.path.insert(0, app_dir + '/gencbilisim_api')

# Sanal ortamı etkinleştirin
site_packages = app_dir + '/gencbilisim_api/venv/lib/python3.8/site-packages'
sys.path.insert(1, site_packages)
import site

site.addsitedir(site_packages)

# Uygulama örneğini alın
from gencbilisim_api import app as application
