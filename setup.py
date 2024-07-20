from setuptools import setup
setup(
    name = 'cronometer',
    version = '0.1.0',
    packages = ['cronometer'],
    entry_points = {
        'console_scripts': [
            'cronometer = cronometer.main:main'
        ]
    })