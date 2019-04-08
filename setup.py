# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re, ast

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in promo_rule/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('promo_rule/__init__.py', 'rb') as f:
	version = str(ast.literal_eval(_version_re.search(
		f.read().decode('utf-8')).group(1)))

setup(
	name='promo_rule',
	version=version,
	description='To apply a promotion rule on item groups for providing discoun.',
	author='taherkhalil52@gmail.com',
	author_email='taherkhalil52@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
