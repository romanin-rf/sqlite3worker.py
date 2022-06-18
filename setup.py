import sqlite3worker
import setuptools
import os

setuptools.setup(
    name=sqlite3worker.__name__,
	version=sqlite3worker.__version__,
	description='Allows you to retrieve information about the system.',
	keywords=[sqlite3worker.__name__],
	packages=setuptools.find_packages(),
	author_email=sqlite3worker.__email__,
	url="https://github.com/romanin-rf/sqlite3worker.py",
	long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
	long_description_content_type="text/markdown",
	author='ProgrammerFromParlament',
	license='MIT'
)