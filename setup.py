import re
from setuptools import setup, find_packages

versionPattern = re.compile(r"""^__version__ = ['"](.*?)['"]$""", re.M)
with open("src/fusion_index/_version.py", "rt") as f:
    version = versionPattern.search(f.read()).group(1)


setup(
    name='fusion-index',
    version=version,
    description='Lookup/search index service for Fusion',
    url='https://bitbucket.org/fusionapp/fusion-index',
    install_requires=[
        'Axiom >= 0.7.4',
        'Twisted[tls] >= 15.0.0',
        'characteristic',
        'eliot >= 0.8.0',
        'eliot',
        'fusion_util',
        'hypothesis>=3.0.0,<4.0.0',
        'py2casefold',
        'testtools',
        'toolz',
        'txspinneret >= 0.1.2',
        ],
    license='MIT',
    packages=find_packages(where='src') + ['twisted.plugins'],
    package_dir={'': 'src'},
    include_package_data=True)
