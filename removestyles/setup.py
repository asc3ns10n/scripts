from setuptools import setup

setup(
    name='removestyles',
    version='0.0.4',
    py_modules=['removestyles'],
    install_requires=['ass>=0.5.1', 'tqdm'],
    entry_points={
        "console_scripts": ["removestyles=removestyles:main"]
    }
)
