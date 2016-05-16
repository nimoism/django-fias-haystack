from __future__ import absolute_import, unicode_literals

from setuptools import setup, find_packages

import fias_haystack as meta


def long_description():
    with open('README.rst') as f:
        rst = f.read()
        return rst

setup(
    name='django-fias-haystack',
    version=meta.__version__,
    description=meta.__doc__,
    author=meta.__author__,
    author_email=meta.__contact__,
    long_description=long_description(),
    url='https://github.com/nimoism/django-fias-haystack',
    platforms=["any"],
    packages=find_packages(),
    scripts=[],
    install_requires=[
        'django-appconf',
        'django',
        'django-fias',
        'django-haystack',
    ],
    extras_require={
        'elasticsearch': ['elasticstack', ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]

)
