# Gencbilisim.net API

## Installation
- run ``` cp .env.sample .env``` and fill env variables
- python3 -m venv venv
- source venv/bin/activate
- pip install . 
- run-setup

## Apache 
- touch .htaccess
- chmod -Rf 775 ../gencbilisim_api/
- chown -Rf www-data:www-data ../gencbilisim_api/
- create apache2 conf file

 ```
 VirtualHost *:80>
    ServerName api.yourdomain.net
    ServerAdmin admin@yourdomain.net

    WSGIDaemonProcess gencbilisim_api user=www-data group=www-data threads=5
    WSGIScriptAlias / <path to host directory>/gencbilisim_api/gencbilisim_api.wsgi

    <Directory <path to host directory>/gencbilisim_api>
        WSGIProcessGroup gencbilisim_api
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/api.yourdomain.net_error.log
    CustomLog ${APACHE_LOG_DIR}/api.yourdomain.net_access.log combined

</VirtualHost>
```

## Local
- flask --app gencbilisim_api run
- Navigate to http://localhost:5000/. The app will automatically reload if you change any of the source files.