from setuptools import setup

setup(
    name='Pyped',
    version='1.2',
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
    install_requires=['minibelt', 'arrow', 'requests', 'path.py'],
    entry_points={
        'console_scripts': ['pyp = pyped:main'],
     },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)
