import re
from setuptools import setup

version = ''
with open('sqon/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='sqon',
    version=version,
    description='Python bindings for libsqon',
    author='David McMackins II',
    author_email='david@delwink.com',
    url='http://delwink.com/software/libsqon.html',
    packages=['sqon'],
    package_data={'': ['COPYING']},
    package_dir={'sqon': 'sqon'},
    include_package_data=True,
    license='AGPLv3'
)
