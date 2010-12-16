# Copyright 2009-2010, BlueDynamics Alliance - http://bluedynamics.com

from setuptools import setup, find_packages
import sys, os

version = '1.1'
shortdesc = \
'Documenation of YAFOWIL - Yet Another Form Widget Lib'
longdesc = ""

tests_require = ['interlude']

setup(name='yafowil.documentaion',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
      ],
      keywords='html input widgets form compound array',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'https://github.com/bluedynamics/yafowil',
      license='BSD simplified and CC-BY-SA',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'yafowil',
          # add-on widgets to document
          'yafowil.widget.dynatree',
      ],
      tests_require=tests_require,
      test_suite="yafowil.tests.test_suite",
      extras_require = dict(
          test=tests_require,
      ),
)
