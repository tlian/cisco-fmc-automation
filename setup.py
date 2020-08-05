import codecs
import os

from setuptools import (
    setup,
    find_packages
)
from fmc_auto_modules import (
    __author__,
    __version__,
    __license__
)


def long_description():
    if not (os.path.isfile('README.md') and os.access('README.md', os.R_OK)):
        return ''
    with codecs.open('README.md', encoding='utf8') as f:
        return f.read()


setup(
    name='fmc_auto_modules',
    version=__version__,
    description='Consume Cisco Firepower Management Center RESTful APIs',
    long_description=long_description(),
    url='https://github.com/tlian/cisco-fmc-automation',
    author=__author__,
    author_email='',
    license=__license__,
    entry_points={
        'console_scripts': [
            'avi-create-object = fmc_auto_modules.cli.create_objects:main',
            'avi-nat = fmc_auto_modules.cli.config_natrules:main'
        ]
    },
    packages=find_packages(),
    extras_require={
        ':python_version == "3.7"' : ['argparse>=1.2.1']
    },
    install_requires=[
        'requests>=2.22.0,<3'
    ]
)
