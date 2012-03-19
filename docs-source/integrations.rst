Integrations
============

Basics
------

By importing ``yafowil.loader`` all registrations are done using the
entry-points provided by add-on widgets and integration packages.

CSS and Javascript resources needed by the add-on widgets are available through
entry_point registration. For convinience ``yafowil.utils`` offers functions
to access the relevant information.

Framework integration is about plugging in methods for request uniformation and
i18n bindings to yafowil. Its usally done by registering a global preprocessor
to the factory.


WebOb based frameworks
----------------------

The package ``yafowil.webob`` provides binding to ``WebOb`` based frameworks,
such as ``Pyramid``, ``Google Appengine`` and others.

Setting a dependency to the package in code, i.e. in the custom eggs
``setup.py`` or in ``buildout.cfg`` - whatever is choosed -, is needed.


Zope 2/ Plone based usage
-------------------------

Package ``yafowil.zope2`` handles integration for Zope 2 and Plone.

Setting a dependency to the package in code, i.e. in the custom eggs
``setup.py`` or in ``buildout.cfg`` - whatever is choosed -, is needed.

In ``portal_setup`` or in site-setup ``add-ons`` install YAFOWIL.

The example
`YAFOWIL tutorial at plone.org <http://plone.org/documentation/kb/build-a-custom-search-form-with-yafowil>`_
explains how to build a custom search form using YAFOWIL.

