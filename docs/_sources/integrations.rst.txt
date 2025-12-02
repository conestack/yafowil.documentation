============
Integrations
============

Basics
------

Import ``yafowil.loader`` to register all blueprints via entry-points:

.. code-block:: python

    import yafowil.loader

Framework integration binds request handling and i18n to YAFOWIL, typically
via global preprocessors registered with the factory.


WebOb-based Frameworks
----------------------

The package ``yafowil.webob`` provides bindings for WebOb-based frameworks
like Pyramid and Google App Engine.

.. code-block:: bash

    pip install yafowil.webob


Zope 2 / Plone
--------------

The package ``yafowil.plone`` handles integration for Zope 2 and Plone.
Install via ``portal_setup`` or in site-setup add-ons.

.. code-block:: bash

    pip install yafowil.plone


Bootstrap Styling
-----------------

The package ``yafowil.bootstrap`` provides Twitter Bootstrap resources
and widget configuration for responsive layouts.

.. code-block:: bash

    pip install yafowil.bootstrap


Treibstoff
----------

The package ``treibstoff`` extends widget functionality with special handling
for AJAX environments. When present, widgets automatically gain additional
behaviors.

.. code-block:: bash

    pip install treibstoff
