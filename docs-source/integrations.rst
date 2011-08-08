Integrations
============

Basics
------

Framework integration is about plugging in methods for request uniformation and
i18n bindings to yafowil. Its done by registering a global preprocessor to the
factory.

WebOb based frameworks
----------------------

The package ``yafowil.webob`` provides binding to ``WebOb`` based frameworks,
such as ``Pyramid``, ``Google Appengine`` and others.

Setting a dependency to the package in code, i.e. in the custom eggs
``setup.py`` or in ``buildout.cfg`` - whatever is choosed -, is needed.

Then ``import yafowil.webob`` after the ``yafowil.loader`` and its done.


Zope 2 based usage
------------------

Package ``yafowil.zope2`` handles integration for Zope 2.

Setting a dependency to the package in code, i.e. in the custom eggs
``setup.py`` or in ``buildout.cfg`` - whatever is choosed -, is needed.

Then ``import yafowil.zope2`` after the ``yafowil.loader`` and its done.

Usage within Plone
------------------

This works like Zope 2 usage. The
`YAFOWIL tutorial at plone.org <http://plone.org/documentation/kb/build-a-custom-search-form-with-yafowil>`_
explains how to build a custom search form using YAFOWIL.