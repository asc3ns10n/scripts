from setuptools import setup

setup(
    name='syncaudio',
    version='0.0.2',
    py_modules=['syncaudio'],
    install_requires=['numpy','scipy','pymkv @ git+https://github.com/asc3ns10n/pymkv.git#egg=pymkv'],
    entry_points={
        "console_scripts": ["syncaudio=syncaudio:main"]
    }
)