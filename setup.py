from setuptools import setup, find_packages
from os import listdir
from os.path import join, dirname, isfile
import mi_e20
import sys

sys.path.insert(0, "mi_e20")

setup(
	name='mi_e20',
	version= '0.8.5',
	packages=find_packages(),
	long_description=open(join(dirname(__file__), 'README.md')).read(),
	entry_points={
		'console_scripts': [
			'mi_e20 = mi_e20.app:main',
			'mi_e20_core = mi_e20.core:main'
			]
		},
	install_requires=[
		'python-miio',
		'PyQt5'
	],
	data_files = [
		('mi_e20/template', ['mi_e20/template/app.ui', 'mi_e20/template/row.ui', 'mi_e20/template/about.ui']),
		('mi_e20', ['mi_e20/config.ini', 'mi_e20/ru.pkg', 'mi_e20/english.pkg'])
	],
	include_package_data=True
)
