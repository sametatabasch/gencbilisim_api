from distutils.core import setup

setup(
    name='gencbilisim_api',
    version='1.0.0',
    packages=[''],
    url='',
    license='',
    author='sametatabasch',
    author_email='sametatabasch@gmail.com',
    description='',
    install_requires=[
        'Flask',
        'flask-cors',
        'python-dotenv',
        'Werkzeug',
        'flask_jwt_extended'
    ],
    entry_points={
        'console_scripts': [
            'create-api-database = create_database:main',
        ],
    },
)
