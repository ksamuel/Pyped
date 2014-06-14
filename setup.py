
import sys
import subprocess

from setuptools import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, 'runtests.py', 'tests.py'])
        raise SystemExit(errno)


setup(
    name='Pyped',
    cmdclass = {'test': PyTest},
    version='1.4',
    author='Kevin Samuel',
    author_email='kevin.samuel@yandex.com',
    py_modules=['pyped'],
    license='GPL2',
    long_description=open('README.md').read(),
    description="Replace sed/grep/cut/awk by letting you execute Python "
                 "one-liners in your ordinary shell, like perl does.",
    url='http://github.com/ksamuel/Pyped',
    keywords="python, pipe",
    include_package_data=True,
    install_requires=['minibelt', 'arrow', 'requests', 'path.py', "six"],
    entry_points={
        'console_scripts': ['pyp = pyped:main'],
     },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
