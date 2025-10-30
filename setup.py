from setuptools import find_packages
from setuptools import setup


version = '2.3.3'
shortdesc = 'Documentation of YAFOWIL - Yet Another Form Widget Library'
longdesc = "See http://docs.yafowil.info"


setup(
    name='yafowil.documentation',
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
    author='Yafowil Contributors',
    author_email='dev@conestack.org',
    url=u'http://github.com/conestack/yafowil.documentation',
    license='Simplified BSD and CC-BY-SA',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['yafowil'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'collective.sphinx.includedoc',
        'sphinxcontrib.jquery', # sphinx dropped jQuery support in version 6.0
        'pillow<=9.5.0',
        'setuptools',
        'sphinx',
        'sphinx_conestack_theme',
        'yafowil<4.0.0',
        'yafowil.widget.ace<2.0.0',
        'yafowil.widget.array<2.0.0',
        'yafowil.widget.autocomplete<2.0.0',
        'yafowil.widget.chosen<2.0.0',
        'yafowil.widget.cron<2.0.0',
        'yafowil.widget.datetime<2.0.0',
        'yafowil.widget.dict<2.0.0',
        'yafowil.widget.image<2.0.0',
        'yafowil.widget.location<2.0.0',
        'yafowil.widget.multiselect<2.0.0',
        'yafowil.widget.richtext<2.0.0',
        'yafowil.widget.select2<2.0.0',
        'yafowil.widget.slider<2.0.0',
        'yafowil.widget.wysihtml5<2.0.0',
        'yafowil.yaml<3.0.0'
    ])
