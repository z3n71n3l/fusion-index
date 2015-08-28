import re
from setuptools import setup, find_packages

versionPattern = re.compile(r"""^__version__ = ['"](.*?)['"]$""", re.M)
with open("fusion_index/_version.py", "rt") as f:
    version = versionPattern.search(f.read()).group(1)


setup(
    name='fusion-index',
    version=version,
    description='Lookup/search index service for Fusion',
    url='https://bitbucket.org/fusionapp/fusion-index',
    install_requires=[
        'Twisted[tls] >= 15.0.0',
        'txspinneret >= 0.1.2',
        'Axiom >= 0.7.4',
        'eliot >= 0.8.0',
        'testtools',
        'characteristic',
        'hypothesis',
        ],
    license='MIT',
    packages=find_packages() + ['axiom.plugins'],
    include_package_data=True)
