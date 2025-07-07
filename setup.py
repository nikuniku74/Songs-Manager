from setuptools import setup

APP = ['app.py']
OPTIONS = {
    'includes': ['flask', 'webbrowser', 'socket', 'threading'],
    'packages': ['requests'],  # << QUI va requests
    'resources': ['templates'],
    'plist': {
        'CFBundleName': 'SongApp',
    }
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
