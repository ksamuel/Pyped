# -*- coding: utf-8 -*-


import os
from setuptools import setup, find_packages


open('MANIFEST.in', 'w').write('\n'.join((
    "include *.txt *.md",
)))

setup(
    name='Pyped',
    version='1.0',
    author='Kevin Samuel',
    author_email='kevin.samuel@yandex.com',
    py_modules=['pyped'],
    license='GPL2',
    long_description=open('README.md').read(),
    description='Command that pipes data from bash to Python, and vice-versa',
    url='http://github.com/ksamuel/Pyped',
    keywords="python, pipe",
    include_package_data=True,
    install_requires=['minibelt', 'arrow', 'requests', 'path.py'],
    entry_points={
        'console_scripts': ['py = pyped:main'],
     },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
