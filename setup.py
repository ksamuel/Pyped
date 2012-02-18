from setuptools import setup, find_packages

setup(
    name='Pyped',
    version='0.1',
    author='Kevin Samuel',
    author_email='kevin@yeleman.com',
    packages=find_packages(),
    license='Command that pipes data from bash to Python, and vice-versa',
    long_description=open('README').read(),
    provides=['py'],
    description='Text based but human and VCS friendly task manager',
    url='http://github.com/ksamuel/Pyped',
    keywords="python, pipe",
    include_package_data=True,
    scripts=['bin/py'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)