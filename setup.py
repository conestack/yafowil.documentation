import os
from setuptools import (
    setup,
    find_packages,
)


version = '2.0.3'
shortdesc = \
'Documentation of YAFOWIL - Yet Another Form Widget Library'
longdesc = "See http://docs.yafowil.info"
tests_require = ['interlude']


setup(name='yafowil.documentation',
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
      keywords='html input widgets form compound',
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
          'Pillow',
          'sphinx',
          'collective.sphinx.includedoc',
          'yafowil',
          'yafowil.yaml',
           # add-on widgets to document
          'yafowil.widget.ace',
          'yafowil.widget.array',
          'yafowil.widget.autocomplete',
          'yafowil.widget.chosen',
          'yafowil.widget.datetime',
          'yafowil.widget.dict',
          'yafowil.widget.dynatree',
          'yafowil.widget.image',
          'yafowil.widget.multiselect',
          'yafowil.widget.richtext',
          'yafowil.widget.select2',
          'yafowil.widget.wysihtml5',
      ],
      tests_require=tests_require,
      test_suite="yafowil.tests.test_suite",
      extras_require = dict(
          test=tests_require,
      ))
