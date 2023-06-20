#! /usr/bin/python3
import sys
import logging
import os
from logging.handlers import RotatingFileHandler

logging.basicConfig(stream=sys.stderr)

app_dir = os.path.dirname(os.path.abspath(__file__))

# Proje ana klasörüne geçiş yapın
sys.path.insert(0, app_dir)

# Sanal ortamı etkinleştirin
site_packages = app_dir + '/venv/lib/python3.8/site-packages'
sys.path.insert(1, site_packages)
import site

site.addsitedir(site_packages)

# dotenv modülünü kullanarak ortam değişkenlerini yükleyin
import dotenv

dotenv.load_dotenv(app_dir + '/.env')
# Uygulama örneğini alın
from gencbilisim_api import app as application
