from setuptools import setup

setup(
    name='create_signs_subs',
    version='0.0.1',
    py_modules=['create_signs_subs'],
    install_requires=['ass'],
    entry_points={
        "console_scripts": ["create_signs_subs=create_signs_subs:main"]
    }
)
