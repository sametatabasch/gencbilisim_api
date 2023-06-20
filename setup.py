from distutils.core import setup


setup(
    name='gencbilisim_api',
    version='1.0.0',
    packages=[''],
    url='https://github.com/sametatabasch/gencbilisim-api',
    license='MIT',
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
            'run-setup = run_setup:main',
        ],
    },
    # bdist_wheel parametresi eklendi
    setup_requires=[
        'wheel',
    ],
)