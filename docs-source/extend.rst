=====================================
Extending YAFOWIL - Custom Blueprints
=====================================

This chapter explains how to create custom blueprints for YAFOWIL.


Blueprint Anatomy
=================

A blueprint is a collection of callables organized in five chains:

**extractors**
    Get, convert, and validate data from the request.

**edit_renderers**
    Generate HTML for edit mode.

**display_renderers**
    Generate HTML for display/read-only mode.

**preprocessors**
    Prepare runtime data before extraction/rendering. Rarely needed.

**builders**
    Modify widget after creation. Rarely needed.

Most custom blueprints only need extractors and renderers. Across 63 blueprint
registrations in the YAFOWIL ecosystem, only 2 use builders and none use
custom preprocessors.

Chains execute in specific orders:

- Extractors: right-to-left (innermost first)
- Renderers: left-to-right (outermost first)
- Preprocessors: left-to-right


Writing Extractors
==================

An extractor validates and transforms data from the request.

Signature:

.. code-block:: python

    def my_extractor(widget, data):
        # Access previous extractor's result
        value = data.extracted

        # Access request data
        raw = data.request.get(widget.dottedpath)

        # Validate and transform
        if not valid(value):
            raise ExtractionError('Invalid value')

        return transformed_value

Key points:

- Return the extracted/transformed value
- Access previous result via ``data.extracted``
- Raise ``ExtractionError`` for validation failures
- Use ``abort=True`` to stop the chain, ``abort=False`` to continue

.. code-block:: python

    from yafowil.base import ExtractionError

    def validate_positive(widget, data):
        value = data.extracted
        if value is not None and value < 0:
            raise ExtractionError('Must be positive', abort=False)
        return value


Writing Renderers
=================

Renderers generate HTML output.

Signature:

.. code-block:: python

    def my_renderer(widget, data):
        # Access HTML tag helper
        tag = data.tag

        # Access previous renderer's output
        inner = data.rendered

        # Build HTML
        return tag('div', inner, class_='wrapper')

Edit vs Display Renderers
-------------------------

- **edit_renderers**: Generate form inputs for editing
- **display_renderers**: Generate read-only display markup

Both have the same signature but different purposes.

Utility Functions
-----------------

.. code-block:: python

    from yafowil.utils import (
        attr_value,    # Get widget attribute, call if callable
        cssid,         # Generate CSS ID
        cssclasses,    # Build CSS class string
    )

    def my_renderer(widget, data):
        tag = data.tag
        max_val = attr_value('max_value', widget, data, default=100)
        return tag('input',
            type='number',
            max=max_val,
            id=cssid(widget, 'input'),
            class_=cssclasses(widget, data),
        )


The @managedprops Decorator
===========================

The ``@managedprops`` decorator declares which properties a callable uses.
This enables automatic documentation generation.

.. code-block:: python

    from yafowil.utils import managedprops

    @managedprops('max_value', 'min_value', 'class')
    def range_extractor(widget, data):
        value = data.extracted
        max_val = attr_value('max_value', widget, data, default=100)
        min_val = attr_value('min_value', widget, data, default=0)
        if value < min_val or value > max_val:
            raise ExtractionError(f'Value must be between {min_val} and {max_val}')
        return value

Apply to both extractors and renderers that use widget properties.


Documenting Properties
======================

Register documentation for auto-generated reference:

.. code-block:: python

    from yafowil.base import factory

    # Blueprint description
    factory.doc['blueprint']['mywidget'] = """\
    Custom widget for special input.
    """

    # Property descriptions
    factory.doc['props']['mywidget.max_value'] = """\
    Maximum allowed value.
    """

    # Default values
    factory.defaults['mywidget.max_value'] = 100

The ``@managedprops`` decorator links properties to their callables,
enabling the documentation system to show which functions use each property.


Registering Blueprints
======================

Register with the factory:

.. code-block:: python

    factory.register(
        'mywidget',
        extractors=[my_extractor],
        edit_renderers=[my_edit_renderer],
        display_renderers=[my_display_renderer],
    )

Name restrictions: Blueprint names cannot contain ``*``, ``:``, or ``#``.


Complete Example: Rating Widget
===============================

A practical example implementing a star-rating input.

Specification
-------------

- Renders 1-5 radio buttons as stars for edit mode
- Displays filled/empty stars for display mode
- Extracts integer 1-5 from request
- Validates value is in valid range

Implementation
--------------

.. code-block:: python

    from yafowil.base import ExtractionError
    from yafowil.base import factory
    from yafowil.common import generic_extractor
    from yafowil.utils import attr_value
    from yafowil.utils import cssclasses
    from yafowil.utils import cssid
    from yafowil.utils import managedprops


    @managedprops('max_stars')
    def rating_extractor(widget, data):
        """Validate rating is within allowed range."""
        value = data.extracted
        if value in (None, ''):
            return None
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ExtractionError('Invalid rating value')
        max_stars = attr_value('max_stars', widget, data, default=5)
        if not 1 <= value <= max_stars:
            raise ExtractionError(f'Rating must be between 1 and {max_stars}')
        return value


    @managedprops('max_stars', 'class')
    def rating_edit_renderer(widget, data):
        """Render rating as radio button group."""
        tag = data.tag
        max_stars = attr_value('max_stars', widget, data, default=5)
        current = data.value if data.value is not None else 0
        name = widget.dottedpath

        inputs = []
        for i in range(1, max_stars + 1):
            checked = 'checked' if i == current else None
            inp = tag('input',
                type='radio',
                name=name,
                value=str(i),
                checked=checked,
            )
            label = tag('label', inp, f' {i} star{"s" if i > 1 else ""}')
            inputs.append(label)

        return tag('div',
            '\n'.join(inputs),
            id=cssid(widget, 'rating'),
            class_=cssclasses(widget, data),
        )


    @managedprops('max_stars')
    def rating_display_renderer(widget, data):
        """Render rating as filled/empty stars."""
        tag = data.tag
        max_stars = attr_value('max_stars', widget, data, default=5)
        value = data.value if data.value is not None else 0

        stars = []
        for i in range(1, max_stars + 1):
            star = '\u2605' if i <= value else '\u2606'  # ★ or ☆
            stars.append(star)

        return tag('span', ''.join(stars), class_='rating-display')


    # Register the blueprint
    factory.register(
        'rating',
        extractors=[generic_extractor, rating_extractor],
        edit_renderers=[rating_edit_renderer],
        display_renderers=[rating_display_renderer],
    )

    # Document the blueprint
    factory.doc['blueprint']['rating'] = """\
    Star rating input widget. Renders radio buttons for selection
    and displays filled/empty stars in display mode.
    """

    factory.defaults['rating.max_stars'] = 5
    factory.doc['props']['rating.max_stars'] = """\
    Maximum number of stars (default 5).
    """


Tests
-----

.. code-block:: python

    import unittest
    from yafowil.base import factory


    class TestRatingBlueprint(unittest.TestCase):

        def test_edit_renderer_empty(self):
            widget = factory('rating', name='score')
            html = widget()
            self.assertIn('id="rating-score"', html)
            self.assertIn('type="radio"', html)
            self.assertIn('name="score"', html)
            # No radio should be checked
            self.assertNotIn('checked', html)

        def test_edit_renderer_with_value(self):
            widget = factory('rating', name='score', value=3)
            html = widget()
            self.assertIn('value="3" checked', html)

        def test_display_renderer(self):
            widget = factory('rating', name='score', value=3, props={
                'mode': 'display',
            })
            html = widget()
            self.assertIn('\u2605\u2605\u2605\u2606\u2606', html)  # ★★★☆☆

        def test_extractor_valid(self):
            widget = factory('rating', name='score')
            data = widget.extract({'score': '4'})
            self.assertEqual(data.extracted, 4)
            self.assertFalse(data.errors)

        def test_extractor_empty(self):
            widget = factory('rating', name='score')
            data = widget.extract({'score': ''})
            self.assertIsNone(data.extracted)
            self.assertFalse(data.errors)

        def test_extractor_invalid_type(self):
            widget = factory('rating', name='score')
            data = widget.extract({'score': 'abc'})
            self.assertTrue(data.errors)
            self.assertIn('Invalid rating', str(data.errors[0]))

        def test_extractor_out_of_range(self):
            widget = factory('rating', name='score')
            data = widget.extract({'score': '10'})
            self.assertTrue(data.errors)
            self.assertIn('must be between', str(data.errors[0]))

        def test_custom_max_stars(self):
            widget = factory('rating', name='score', props={'max_stars': 10})
            data = widget.extract({'score': '8'})
            self.assertEqual(data.extracted, 8)
            self.assertFalse(data.errors)


Packaging for Distribution
==========================

Structure your package in the ``yafowil.widget.*`` namespace:

.. code-block:: text

    yafowil.widget.rating/
    ├── pyproject.toml
    └── src/
        └── yafowil/
            └── widget/
                └── rating/
                    ├── __init__.py
                    └── widget.py

Entry Point Registration
------------------------

In ``pyproject.toml``, register the entry point:

.. code-block:: toml

    [project.entry-points."yafowil.plugin"]
    "yafowil.widget.rating" = "yafowil.widget.rating:register"

In ``__init__.py``, define the register function with the ``@entry_point``
decorator. This function registers both blueprints and resources:

.. code-block:: python

    import os
    import webresource as wr
    from yafowil.base import factory
    from yafowil.utils import entry_point

    resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

    # Define resources (optional - only if widget needs JS/CSS)
    resources = wr.ResourceGroup(
        name='yafowil.widget.rating',
        directory=resources_dir,
        path='yafowil-rating'
    )
    resources.add(wr.ScriptResource(
        name='yafowil-rating-js',
        directory=resources_dir,
        path='yafowil-rating',
        resource='widget.js',
        compressed='widget.min.js'
    ))
    resources.add(wr.StyleResource(
        name='yafowil-rating-css',
        directory=resources_dir,
        path='yafowil-rating',
        resource='widget.css',
        compressed='widget.min.css'
    ))

    @entry_point(order=10)
    def register():
        # Import triggers blueprint registration in widget.py
        from yafowil.widget.rating import widget  # noqa

        # Register resources for default theme (optional)
        factory.register_resources('default', 'yafowil.widget.rating', resources)

This ensures your blueprint is registered when ``yafowil.loader`` is imported.
