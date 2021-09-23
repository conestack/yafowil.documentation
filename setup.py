from setuptools import find_packages
from setuptools import setup


version = '2.2.dev0'
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
        'setuptools',
        'pillow',
        'sphinx',
        'collective.sphinx.includedoc',
        'sphinx_bootstrap_theme',
        'yafowil',
        'yafowil.yaml',
        # add-on widgets to document
        # 'yafowil.widget.alohaeditor',
        'yafowil.widget.ace',
        'yafowil.widget.array',
        'yafowil.widget.autocomplete',
        'yafowil.widget.chosen',
        'yafowil.widget.cron',
        'yafowil.widget.datetime',
        'yafowil.widget.dict',
        # 'yafowil.widget.dynatree',
        'yafowil.widget.image',
        'yafowil.widget.location',
        'yafowil.widget.multiselect',
        # 'yafowil.widget.recaptcha',
        'yafowil.widget.richtext',
        'yafowil.widget.select2',
        'yafowil.widget.slider',
        'yafowil.widget.wysihtml5',
    ])
