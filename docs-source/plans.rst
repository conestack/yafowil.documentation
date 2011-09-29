=====
Plans
=====

Plans are a sets of blueprints. Plans are an abbreviation or shortcuts
to build commonly used combinations of blueprints using the factory.

To indicate a plan the prefix ``#`` is used. I.e. ``#stringfield`` is
registered as a plan and expands to ``field:label:error:text``.

Plans can be combined with other registered blueprints and custom blueprints
too, i.e. ``*myvalidatingextractor:#numberfieldfield`` expands to
``*myvalidatingextractor:field:label:error:text``.

It is possible to register own plans to the factory, i.e. like so::

    >>> from yafowil.base import factory
    >>> factory.register_plan('divstringfield', 'field:label:error:div:text')
    >>> mywidget = factory('#divstringfield')
    
Its also possible to overwrite already registered plans.

The following plans are pre-registered. The table is auto-generated and so it
shows all registation from the installed packages when the documentation was
generated.

.. yafowilplans::
