#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages
import gitserver
from gitserver.utils import refresh_plugin_cache

here = os.path.abspath(os.path.dirname(__file__))


def strip_comments(l):
    return l.strip()
    #return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), 'requirements', *f)).readlines()]))

install_requires = reqs('default.txt')

tests_require = []
docs_extras = reqs('docs.txt')
testing_extras = tests_require + reqs('testing.txt')

readme = open(os.path.join(here, 'README.rst')).read()
history = open(os.path.join(here, 'HISTORY.rst')).read().replace('.. :changelog:', '')

packages = find_packages()
packages.append('twisted.plugins')

setup(
    name='gitserver',
    version=gitserver.__version__,
    description='git server',
    long_description=readme + '\n\n' + history,
    author='Adam Venturella <aventurella@gmail.com>',
    author_email='aventurella@gmail.com',
    url='https://github.com/aventurella/gitserver',
    packages=packages,
    package_data={
        'twisted': ['plugins/gitserver.py'],
    },
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        'docs': docs_extras,
    },
    tests_require=tests_require,
    license="BSD",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'gitserver.driver': [
            'example = gitserver.example',
        ],
    }
)

refresh_plugin_cache()
