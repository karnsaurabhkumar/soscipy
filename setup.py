# read the contents of your README file
from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='soscipy',
    packages=find_packages(),
    version='0.0.21',
    description='A python library to help do reproducible research in social sciences',
    author='Saurabh Karn',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='test',
    long_description=long_description,
    long_description_content_type="text/markdown"
)
