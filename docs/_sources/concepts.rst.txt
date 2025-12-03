=============
Core Concepts
=============

YAFOWIL is built on a few core ideas:

1. Runtime rules over static configuration
2. Framework-agnostic design
3. Simple, Pythonic callables instead of class inheritance
4. No coupling to storage
5. Chains and trees as structures


Widget
======

A YAFOWIL form is a tree of widgets. Everything called a "field" in other
libraries is a widget. Widgets can have children - fieldsets and forms
are also widgets.

Widget behavior is defined by blueprints and properties. The widget class
is generic and never instantiated directly - use the factory instead.

Widgets provide a dict-like API for building compounds:

.. code-block:: python

    form = factory('form', name='myform', props={'action': '/submit'})
    form['field1'] = factory('text')
    form['fieldset'] = factory('fieldset')
    form['fieldset']['nested'] = factory('text')


RuntimeData
===========

During a request-response cycle, widget state is held in RuntimeData.
It collects values, request data, errors, and rendered HTML for each widget.

Key attributes:

- ``value`` - The initial/persisted value
- ``extracted`` - The value extracted from request
- ``errors`` - List of ExtractionErrors
- ``rendered`` - The rendered HTML output
- ``request`` - Reference to the request object

Access via path:

.. code-block:: python

    data.fetch('myform.fieldset.nested').extracted


Controller
==========

The Controller orchestrates form processing:

.. code-block:: python

    controller = Controller(form, request)

It immediately processes the form upon initialization:

- ``controller.rendered`` - The rendered form HTML
- ``controller.data`` - The RuntimeData tree


Factory
=======

The factory is a singleton registry that creates widgets from blueprints:

.. code-block:: python

    from yafowil.base import factory

    widget = factory('text', props={'class': 'input-text'})

For root widgets, provide a name:

.. code-block:: python

    form = factory('form', name='myform', props={'action': '/submit'})


Blueprint Chains
----------------

Blueprints can be chained using colon-separated names:

.. code-block:: python

    widget = factory('field:label:error:text')

This combines the rendering and extraction logic of all named blueprints.

To address properties for a specific blueprint, prefix with the blueprint name:

.. code-block:: python

    widget = factory('field:label:text', props={
        'label': 'My Field',
        'label.class': 'label-class',  # Only affects 'label' blueprint
    })


Macros
------

Macros are predefined blueprint chains. Use the ``#`` prefix:

.. code-block:: python

    widget = factory('#field:text')  # Expands 'field' macro


Custom Blueprints
-----------------

Inject custom behavior using the ``*`` prefix:

.. code-block:: python

    def my_validator(widget, data):
        if data.extracted != 'expected':
            raise ExtractionError('Invalid value')
        return data.extracted

    widget = factory('field:*validate:text', custom={
        'validate': {'extractors': [my_validator]},
    })


Chains
======

Blueprints consist of five chains of callables:

Extractors
    Get, convert, and validate data from the request. Executed right-to-left
    during extraction. Raise ``ExtractionError`` on validation failure.

Edit Renderers
    Generate HTML for edit mode. Executed left-to-right. Each receives
    the previous renderer's output in ``data.rendered``.

Display Renderers
    Generate HTML for display mode. Same execution as edit renderers.

Preprocessors
    Run once before extraction/rendering. Used for framework integration
    (request wrapping, i18n setup). Rarely needed in custom blueprints.

Builders
    Run once at widget creation time. Used to auto-populate compound
    widgets with children. Rarely needed in custom blueprints.


Validation
==========

Extraction and validation happen together. If validation fails, raise
``ExtractionError``:

.. code-block:: python

    from yafowil.base import ExtractionError

    def validate_positive(widget, data):
        if data.extracted < 0:
            raise ExtractionError('Value must be positive')
        return data.extracted

The ``abort`` parameter controls chain behavior:

.. code-block:: python

    raise ExtractionError('message', abort=True)   # Stop extraction chain
    raise ExtractionError('message', abort=False)  # Continue chain


Rendering Modes
===============

Widgets support three modes via the ``mode`` property:

``edit``
    Default. Renders form inputs using edit_renderers.

``display``
    Read-only display using display_renderers.

``skip``
    Renders empty string.

.. code-block:: python

    widget = factory('text', props={'mode': 'display'})

    # Or dynamically
    def get_mode(widget, data):
        return 'display' if user.readonly else 'edit'

    widget = factory('text', props={'mode': get_mode})
