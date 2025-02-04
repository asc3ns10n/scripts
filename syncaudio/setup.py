from setuptools import setup

setup(
    name='syncaudio',
    version='0.0.3',
    py_modules=['syncaudio'],
    install_requires=['numpy','scipy','pymkv2'],
    entry_points={
        "console_scripts": ["syncaudio=syncaudio:main"]
    }
)