from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in moe_files/__init__.py
from moe_files import __version__ as version

setup(
	name='moe_files',
	version=version,
	description='moe_files',
	author='shahzadnaser',
	author_email='shahzadnaser1122@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
