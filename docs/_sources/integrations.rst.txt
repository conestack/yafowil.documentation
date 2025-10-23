Integrations
============

Basics
------

By importing ``yafowil.loader`` all registrations are done using the
entry-points provided by add-on widgets and integration packages.

CSS and JavaScript resources needed by the add-on widgets are available through
``entry_point`` registration. For convenience, ``yafowil.utils`` offers functions
to access the relevant information.

Framework integration is about plugging in methods for request information and
i18n bindings to YAFOWIL. It's usually done by registering a global preprocessor
to the factory.

Setting a dependency to the integration package in code, e.g. in the custom eggs
``setup.py`` or in ``buildout.cfg`` - whatever is chosen -, is needed.


WebOb-based frameworks
----------------------

The package ``yafowil.webob`` provides binding to ``WebOb`` based frameworks,
such as ``Pyramid``, ``Google Appengine`` and others.


Zope 2 / Plone based usage
--------------------------

The package ``yafowil.plone`` handles integration for Zope 2 and Plone.
Install YAFOWIL in ``portal_setup`` or in site-setup ``add-ons``.

The example
`YAFOWIL tutorial at plone.org 
<http://plone.org/documentation/kb/build-a-custom-search-form-with-yafowil>`_
explains how to build a custom search form using YAFOWIL.

.. todo:: this is now only in the Internet Archive


Werkzeug based frameworks
-------------------------

The package ``yafowil.werkzeug`` provides bindings to ``Werkzeug``-based
frameworks, such as ``Flask`` or ``tipfy``.


Bootstrap Styles
----------------

The package ``yafowil.bootstrap`` ships with twitter bootstrap resources and
provides common widget configuration to provide a pretty look and feel and 
responsive layout.


Treibstoff
----------

The package ``treibstoff`` extends widget functionality with special handling, e.g.
for ts.ajax environments.
When treibstoff is present, widgets are automatically registered and gain
additional behaviors.
