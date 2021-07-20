#!/usr/bin/env python3

from setuptools import setup

def get_version():
    return '1.0.0'

if __name__ == "__main__":
    setup(
        name='python-phycam-margin-analysis',
        version=get_version(),
        description='Python phyCAM MARGIN ANALYSIS',
        packages=['src'],
        author='PHYTEC Germany, Mainz',
        author_email='b.feldmann@phytec.de',
        classifiers=[
            'Development Status :: 4 - Beta',
            #'License ::  :: ',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        python_requires='>=3.6',
        install_requires=['smbus'],
        entry_points={},
        include_package_data=True,
    )
