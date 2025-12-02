==========
Quickstart
==========

This guide helps you get started with YAFOWIL quickly.


Installation
============

Install YAFOWIL using pip:

.. code-block:: bash

    pip install yafowil

For framework integration, install the appropriate package:

.. code-block:: bash

    pip install yafowil.webob      # Pyramid, WebOb-based frameworks
    pip install yafowil.werkzeug   # Flask, Werkzeug-based frameworks
    pip install yafowil.plone      # Plone/Zope 2
    pip install yafowil.bootstrap  # Bootstrap styling


Basic Form Example
==================

Import and initialize:

.. code-block:: python

    import yafowil.loader
    from yafowil.base import factory
    from yafowil.controller import Controller

Create a form:

.. code-block:: python

    form = factory(
        'form',
        name='myform',
        props={
            'action': 'http://example.com/submit',
        })

    form['name'] = factory(
        'field:label:text',
        props={
            'label': 'Your Name',
        })

    def save(widget, data):
        print(f"Name: {data.fetch('myform.name').extracted}")

    form['submit'] = factory(
        'submit',
        props={
            'handler': save,
            'action': True,
        })

Render the form:

.. code-block:: python

    html = form()

This produces:

.. code-block:: html

    <form action="http://example.com/submit"
          enctype="multipart/form-data"
          id="form-myform"
          method="post">
        <label for="input-myform-name">Your Name</label>
        <input id="input-myform-name"
               name="myform.name"
               type="text"/>
        <input id="input-myform-submit"
               name="action.myform.submit"
               type="submit"
               value="submit"/>
    </form>


Processing Form Submissions
===========================

Process the form with a request (dict-like mapping):

.. code-block:: python

    request = {
        'myform.name': 'Alice',
        'action.myform.submit': 'submit'
    }
    controller = Controller(form, request)

    # Access extracted data
    data = controller.data
    name = data.fetch('myform.name').extracted  # 'Alice'


Adding Validation
=================

Use the ``required`` property for mandatory fields:

.. code-block:: python

    form['email'] = factory(
        'field:label:error:email',
        props={
            'label': 'Email',
            'required': 'Email is required',
        })

For custom validation, use extractors:

.. code-block:: python

    from yafowil.base import ExtractionError

    def validate_age(widget, data):
        value = data.extracted
        if value and int(value) < 18:
            raise ExtractionError('Must be 18 or older')
        return value

    form['age'] = factory(
        'field:label:error:*agecheck:text',
        props={
            'label': 'Age',
            'datatype': int,
        },
        custom={
            'agecheck': {'extractors': [validate_age]},
        })


Minimal WSGI Application
========================

A complete working example using WebOb:

.. code-block:: python

    import yafowil.loader
    import yafowil.webob
    from yafowil.base import factory
    from yafowil.controller import Controller
    from webob import Request, Response

    def application(environ, start_response):
        request = Request(environ)
        response = Response()

        def save(widget, data):
            name = data.fetch('hello.name').extracted
            response.write(f'<p>Hello, {name}!</p>')

        form = factory('form', name='hello', props={'action': '/'})
        form['name'] = factory('field:label:error:text', props={
            'label': 'Your name',
            'required': True,
        })
        form['submit'] = factory('field:submit', props={
            'handler': save,
            'action': True,
        })

        controller = Controller(form, request)
        response.write(f'<html><body>{controller.rendered}</body></html>')
        return response(environ, start_response)

    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        server = make_server('127.0.0.1', 8080, application)
        print('Serving on http://127.0.0.1:8080')
        server.serve_forever()

Run with:

.. code-block:: bash

    pip install yafowil.webob webob
    python app.py


Next Steps
==========

- :doc:`concepts` - Understanding YAFOWIL's architecture
- :doc:`usage` - Detailed usage patterns
- :doc:`blueprints` - Reference for all available blueprints
- :doc:`extend` - Creating custom blueprints
