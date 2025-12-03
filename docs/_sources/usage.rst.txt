=====
Usage
=====

This chapter covers common usage patterns for YAFOWIL forms.


Widget Trees
============

Forms are organized as widget trees. The form is the root, containing
compounds (fieldsets) and leaves (input fields):

.. code-block:: python

    form = factory('form', name='myform', props={'action': '/submit'})

    form['personal'] = factory('fieldset', props={'legend': 'Personal Info'})
    form['personal']['name'] = factory('field:label:text', props={
        'label': 'Name',
    })
    form['personal']['email'] = factory('field:label:email', props={
        'label': 'Email',
    })

    form['submit'] = factory('submit', props={'action': True})


Data Extraction
===============

After processing, extracted data is available on ``controller.data``:

.. code-block:: python

    request = {
        'myform.personal.name': 'Alice',
        'myform.personal.email': 'alice@example.com',
        'action.myform.submit': 'submit',
    }
    controller = Controller(form, request)

    name = controller.data.fetch('myform.personal.name').extracted
    email = controller.data.fetch('myform.personal.email').extracted


Validation
==========

Required Fields
---------------

Use the ``required`` property:

.. code-block:: python

    form['name'] = factory('field:label:error:text', props={
        'label': 'Name',
        'required': True,  # or a custom message string
    })


Datatype Conversion
-------------------

The ``datatype`` property converts extracted strings:

.. code-block:: python

    form['age'] = factory('field:label:text', props={
        'label': 'Age',
        'datatype': int,
    })

    form['id'] = factory('field:label:text', props={
        'label': 'ID',
        'datatype': uuid.UUID,
    })

Supported by: ``hidden``, ``proxy``, ``text``, ``lines``, ``select``, ``number``.

Use ``emptyvalue`` for non-required fields with datatype:

.. code-block:: python

    form['count'] = factory('field:label:text', props={
        'label': 'Count',
        'datatype': int,
        'emptyvalue': 0,
    })


Custom Validation
-----------------

Inject custom extractors using the ``*`` prefix:

.. code-block:: python

    from yafowil.base import ExtractionError

    def validate_range(widget, data):
        value = data.extracted
        if value is not None and not (0 <= value <= 100):
            raise ExtractionError('Value must be between 0 and 100')
        return value

    form['score'] = factory('field:label:error:*rangecheck:text', props={
        'label': 'Score',
        'datatype': int,
    }, custom={
        'rangecheck': {'extractors': [validate_range]},
    })


Invariants
----------

Cross-field validation uses extractors on parent compounds:

.. code-block:: python

    def xor_validator(widget, data):
        a = data['field_a'].extracted
        b = data['field_b'].extracted
        if bool(a) == bool(b):
            error = ExtractionError('Fill exactly one field')
            data['field_a'].errors.append(error)
            data['field_b'].errors.append(error)
        return data.extracted

    form = factory('*xor:form', name='myform', props={'action': '/'}, custom={
        'xor': {'extractors': [xor_validator]},
    })
    form['field_a'] = factory('field:label:error:text', props={'label': 'A'})
    form['field_b'] = factory('field:label:error:text', props={'label': 'B'})


Persistence
===========

YAFOWIL provides delegation for single-model forms.


Manual Persistence
------------------

Handle extraction manually in the submit handler:

.. code-block:: python

    def save(widget, data):
        model.name = data.fetch('myform.name').extracted
        model.email = data.fetch('myform.email').extracted
        session.commit()


Automatic Persistence
---------------------

Use ``data.write()`` for automatic delegation:

.. code-block:: python

    from yafowil.persistence import attribute_writer

    form = factory('form', name='myform', props={
        'action': '/submit',
        'persist_writer': attribute_writer,
    })
    form['name'] = factory('field:label:text', props={
        'label': 'Name',
        'persist': True,  # Default for most input blueprints
    })

    def save(widget, data):
        data.write(model)  # Writes all persist=True fields to model
        session.commit()

Available writers:

- ``attribute_writer`` - Sets attributes on model
- ``write_mapping_writer`` - Sets dict keys on model
- ``node_attribute_writer`` - Sets node.attrs keys on model


Customizing Persistence
-----------------------

Override target attribute name:

.. code-block:: python

    form['user_name'] = factory('text', props={
        'persist': True,
        'persist_target': 'name',  # Writes to model.name, not model.user_name
    })

Override writer per field:

.. code-block:: python

    form['tags'] = factory('text', props={
        'persist': True,
        'persist_writer': my_custom_writer,
    })


Form Actions
============

Submit buttons trigger handlers when clicked:

.. code-block:: python

    def save_handler(widget, data):
        # Process the form
        pass

    def next_url(request):
        return '/success'

    form['submit'] = factory('submit', props={
        'handler': save_handler,
        'next': next_url,
        'action': True,
    })

Multiple actions:

.. code-block:: python

    form['save'] = factory('submit', props={
        'handler': save_handler,
        'action': 'save',
    })
    form['delete'] = factory('submit', props={
        'handler': delete_handler,
        'action': 'delete',
    })
