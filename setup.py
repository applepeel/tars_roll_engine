import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='roll_engine',
    version='1.0',
    packages=['roll_engine'],
    include_package_data=True,
    license='BSD License',  # example license
    description='Ctrip rollout engine',
    long_description=README,
    url='http://git.dev.sh.ctripcorp.com/tars/django-roll-engine/',
    author='dalang',
    author_email='gxdong@ctrip.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Software Distribution',
    ],
)
