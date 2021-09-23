============
Introduction
============

YAFOWIL targets are rendering form widgets and extracting/validating the data sent
by the browser per widget.

YAFOWIL widgets are just configuration.

It provides a factory which can
produce *widget instances* from *blueprints*.

There is a library of existing blueprints ready to be extended on demand.

YAFOWIL provides blueprints for all HTML standard inputs, lots of helper
blueprints for building complex widgets and a bunch of add-ons (usually in
the namespace ``yafowil.widget.*``).


Motivation
==========

The YAFOWIL authors use several Python frameworks and became very tired of 
inventing widgets again and again. 

YAFOWIL was intentionally written to
be framework-independent. By just feeding it with
configuration it can be used and extended in most existing python web
frameworks. Possible candidates include Zope, Pyramid, Django, Flask, CherryPy and similar.

Another common problem with form libraries is a non-unique look and feel of the
available widget collection. YAFOWIL tries to provide some useful addon widgets,
thereby taking care of a unified user experience.


Dependencies
============

YAFOWIL aims to have no dependencies on any web framework. It utilizes the
`node <http://pypi.python.org/pypi/node>`_
package which provides a powerful abstraction for lightweight graph data structures.

YAFOWIL does not know about data-storage, but offers a hook to add
processing callback handler functions and a mechanism for delegating persistence
automatically (to a certain degree).


Integrations
============

YAFOWIL currently integrates with the following packages:

* `yafowil.plone <http://pypi.python.org/pypi/yafowil.plone>`_
* `yafowil.webob <http://pypi.python.org/pypi/yafowil.webob>`_
* `yafowil.werkzeug <http://pypi.python.org/pypi/yafowil.werkzeug>`_
* `yafowil.bootstrap <http://pypi.python.org/pypi/yafowil.bootstrap>`_

For details refer to the chapter Integrations_.


Example
=======

For the impatient, code says more than 1000 words.

A simple example form works
like so:

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
            'action': 'http://www.domain.tld/someform',
        })

    form['someinput'] = factory(
        'label:text',
        props={
            'label': 'Your Text',
        })

    def formaction(widget, data):
        data.printtree()

    def formnext(request):
        return 'http://www.domain.tld/result'

    form['submit'] = factory(
        'submit',
        props={
            'handler': formaction,
            'next': formnext,
            'action': True,
        })

Render the empty form by calling the form object:

.. code-block:: python

    rendered = form()

This results in:

.. code-block:: html

    <form action="http://www.domain.tld/someform"
          enctype="multipart/form-data"
          id="form-myform"
          method="post">
        <label for="input-myform-someinput">Your Text</label>
        <input id="input-myform-someinput"
               name="myform.someinput"
               type="text"/>
        <input id="input-myform-submit"
               name="action.myform.submit"
               type="submit"
               value="submit" />
    </form>

Process the form with a ``request``.
Requests are expected to be a dict-like mapping:

.. code-block:: python

    request = {
        'myform.someinput': 'Hello World',
        'action.myform.submit': 'submit'
    }
    controller = Controller(form, request)

The result of processing gets written to ``controller.data``::

.. code-block:: python

    controller.data


Creating a widget
=================

A *widget* is an instance of a *blueprint* created by the factory. Factory is a
singleton and operates as a registry for blueprints.

By calling the factory, a widget is created.

Here, a naked text input field from
the ``text`` blueprint:

.. code-block:: python

    widget = factory('text')

Blueprints can be chained by colon-separated names, or given as a list:

.. code-block:: python

    widget = factory('field:label:text')

This causes the created widget to chain the registered renderers, extractors,
and other parts of the named blueprints (``field``, ``label`` and ``text``)
in order.

Blueprint chains can be organised using macros to reduce the complexity of
factory calls (details below). E.g.:

.. code-block:: python

    widget = factory('#errorfield:text')

expands the macro ``#errorfield`` to ``field:label:error`` and appends ``:text`` so
the result is ``field:label:error:text``.


Widget trees
============

YAFOWIL forms are organized as **widget trees**. The entire form is the
root widget which contains compound nodes (which can contain children) and/or
leaf nodes. A widget behaves similarly to an ordered Python dictionary. Compounds
may represent the entire HTML form or fieldsets, while leaf objects may
represent the various HTML input fields.

Building a widget tree:

.. code-block:: python

    form = factory(
        'form',
        name='formname',
        props={
            'action': 'someurl',
        })
    form['somefield'] = factory(
        'field:label:text',
        props={
            'label': 'Some Field',
        })
    form['somefieldset'] = factory(
        'fieldset',
        props={
            'legend': 'A Fieldset',
        })
    form['somefieldset']['innerfield'] = factory(
        'field:label:text',
        props={
            'label': 'Inner Field',
        })
    form['submit'] = factory(
        'submit',
        props={
            'handler': formaction,
            'next': formnext,
            'action': True,
        })


Rendering Mode
==============

The way a widget is rendered is controlled by its mode. Every widget may be given
a ``mode`` keyword argument to the factory as a string or a callable accepting
two parameters (``widget`` and ``data``), and returning a string.

These modes are supported:

``edit``
    Default classic mode, editing of form is possible. Rendering follows the
    registered ``edit_renderers``.

``display``
    No form elements are rendered, just the data as defined by registered
    ``display_renderers``.

``skip``
    Renders an empty string.


Data extraction
===============

After calling the ``Controller`` we have the form processing result on
``controller.data``, which is an instance of ``yafowil.base.RuntimeData``.

Like widgets, runtime-data is organized as tree where each runtime data node
refers to a widget node and provides the extracted value and any error(s) that
occurred while extracting data from the request.

.. code-block:: python

    request = {
        'formname.somefield': 'Hello World',
        'action.formname.submit': 'submit'
    }
    controller = Controller(form, request)

    data = controller.data

    value = data.fetch('myform.someinput').extracted


Validation
==========

In YAFOWIL, validation and extraction happens at the same time. Extraction means
to get a meaningful value out of the request. Validation means to check
constraints, i.e if a number is positive or an email-address is valid.

If validation fails, ``ExtractionErrors`` are collected on runtime-data describing
what happened.


Datatype extraction
-------------------

There is a set of common blueprints where you can define the ``datatype`` of
the extracted value. Datatype is either some primitive type like ``int`` or
``float``, a class object which can be instantiated with the extracted string
value like ``uuid.UUID``, or a callable expecting the extracted string value
and converting it to whatever.

.. code-block:: python

    form['somefield'] = factory('field:label:text', props={
        'label': 'Some Field',
        'datatype': int
    })

Blueprints which provide ``datatype`` by default are ``hidden``, ``proxy``,
``text``, ``lines``, ``select`` and ``number``.

When providing a ``datatype`` to a widget which is not ``required``, we
probably want to have a valid ``emptyvalue``, which takes effect if the request
contains an empty string for this widget. The empty value must either be of
or castable to the defined ``datatype`` or ``UNSET``.

.. code-block:: python

    form['somefield'] = factory('field:label:text', props={
        'label': 'Some Field',
        'datatype': int,
        'emptyvalue': 0
    })

Blueprints which provide ``emptyvalue`` by default are ``hidden``, ``proxy``,
``text``, ``textarea``, ``lines``, ``select``, ``file``, ``password``,
``email``, ``url``, ``search`` and ``number``.


Invariants
----------

Invariants are implemented as extractors on compounds. Usually they are defined as
a custom blueprint (see below) with one extractor on some parent of the elements
to be validated.

Here is a short example (extension of the ``hello world`` example) of a custom
invariant extractor which checks if one or the other field is filled, but never
both or none (XOR):

.. code-block:: python

    from yafowil.base import ExtractionError
    # ... see helloworld example whats missing here

    def myinvariant_extractor(widget, data):
        if data['hello'].extracted == data['world'].extracted:
            error = ExtractionError(
                'provide hello or world, not both or none'
            )
            data['hello'].error.append(error)
            data['world'].error.append(error)
        return data.extracted

    def application(environ, start_response): 
        # ... see helloworld example for the code that belongs here
        form = factory(
            u'*myinvariant:form',
            name='helloworld', 
            props={
                'action': url,
            },
            custom={
                'myinvariant': {
                    'extractors': [myinvariant_extractor]
                }
            })
        form['hello'] = factory(
            'field:label:error:text',
            props={
                'label': 'Enter some text here',
            })
        form['world'] = factory(
            'field:label:error:text',
            props={
                'label': 'OR Enter some text here',
            })
        # ... see helloworld example for the code that belongs here


Persistence
===========

YAFOWIL provides a delegation mechanism for single data model bound forms.

Processing the extracted form data often requires some additional computing and
targets several persistent objects. In this case, we simply implement the submit
action callback and do what's necessary:

.. code-block:: python

    class Form(object):

        def __init__(self, model):
            self.model = model

        def __call__(self, request):
            controller = Controller(self.form, request)

        def save(self, widget, data):
            # HERE IS THE INTERESTING PART
            self.model.hello = data.fetch('myform.hello').extracted
            self.model.world = data.fetch('myform.world').extracted
            # ...
            transaction.commit()

        form = factory(
            'form',
            name='myform',
            props={
                'action': 'http://www.domain.tld/someform',
            })
        form['hello'] = factory(
            'field:label:error:text',
            props={
                'label': 'Enter hello text here',
            })
        form['world'] = factory(
            'field:label:error:text',
            props={
                'label': 'Enter world text here',
            })
        form['submit'] = factory(
            'submit',
            props={
                'handler': save,
                'action': True,
            })

    form = Form(model)
    form(request)
    # ... should have form data persisted to model now

While fetching the value from data and assigning it to model seems quite
reasonable, as long as forms are small, this may get annoying when writing more
or complex forms. If forms refer to a single model, ``data.write`` can be used
to delegate transferring the extracted data to the model.

.. code-block:: python

    from yafowil.persistence import attribute_writer

    class Form(object):

        # ...

        def save(self, widget, data):
            # HERE IS THE INTERESTING PART
            data.write(self.model)
            transaction.commit()

        form = factory(
            'form',
            name='myform',
            props={
                'action': 'http://www.domain.tld/someform',
                'persist_writer': attribute_writer
            })
        # ...

    form = Form(model)
    form(request)

The most common way is to add the ``persist_writer`` property to the entire
form. ``data.write`` will walk through the data tree and call
``attribute_writer`` with ``model``, ``target`` and ``value`` arguments for
each runtime-data node with the ``persist`` property set to ``True``.

The ``persist`` property indicates widgets to be considered when
``data.write`` gets called and is given as part of the widget properties
at factory time.

The ``persist`` property is ``True`` by default on ``hidden``, ``proxy``,
``text``, ``textarea``, ``lines``, ``password``, ``checkbox``, ``select``,
``email``, ``url`` and ``number`` blueprints.

The ``model`` received in persisting callback is the model passed to
``data.write``.

The ``target`` received in the persisting callback is an arbitrary Python object
and defaults to the runtime-data ``name`` for any particular widget.
The target can be customized by providing ``persist_target`` as part of the
widget properties at factory time.

The ``value`` received in the persisting callback is the extracted value from
runtime-data.

The writer callback can be customized for each widget via the ``persist_writer``
property.

``data.write`` can be called with a ``recursive=False`` keyword argument.
In that case, persistence only happens on the calling level.

When setting the ``persist`` property ``True`` on compound widgets, make sure
its children get ``persist`` set to ``False`` explicitly if the used child factory
blueprint is persistent by default.

If ``data.write`` gets called on runtime-data which contains extraction error(s),
a ``RuntimeError`` is raised.

The following default writer callbacks are provided:

* ``yafowil.persistence.attribute_writer``
    Write ``value`` to ``target`` attribute on ``model``.

* ``yafowil.persistence.write_mapping_writer``
    Write ``value`` to ``target`` write mapping key on ``model``.

* ``yafowil.persistence.node_attribute_writer``
    Write ``value`` to ``target`` node.attrs key on ``model``.

In conjunction with ``datatype`` and ``emptyvalue``, this approach gives us a lot of
convenience for persisting form data to single models.


Providing blueprints
====================

General behaviours (rendering, extracting, etc...) can be registered as
blueprints in the factory:

.. code-block:: python

    factory.register(
        'myblueprint', 
        extractors=[myvalidator], 
        edit_renderers=[],
        display_renderers=[],
        preprocessors=[],
        builders=[])

and then used as regular blueprints when calling the factory:

.. code-block:: python

    widget = factory('field:label:myblueprint:text', props={
        'label': 'Inner Field',
    })


Adding custom behaviour
=======================

It's possible to inject custom behaviour by marking a part of the blueprint
chain with the asterisk ``*`` character. Behaviours are one or more
of a:

``extractor``
    extracts, validates and/or converts form-data from the request.

``edit_renderer``
    build the markup for editing.

``display_renderer``
    build the markup for display only.

``builder``
    Generic hook called once at factory time of the widget. Here e.g. subwidgets
    can be created.

``preprocessor``
    Generic hook to prepare runtime-data. Runs once per runtime-data instance
    before extractors or renderers are running.

.. code-block:: python

    def myvalidator(widget, data):
       # validate the data, raise ExtractionError if something's wrong
       if data.extracted != 'something:'
           raise ExtractionError("only 'something' is allowed as input.")
       return data.extracted

    widget = factory(
        'field:label:*myvalidation:text', 
        props={
            'label': 'Inner Field',
        },
        custom={
            'myvalidation': dict(extractor=[myvalidator]),
        })


Delivering resources
====================

YAFOWIL addon widgets are shipped with their required JavaScript and stylesheet
resources. These resources are registered to the factory with additional
information like delivery order and resources group.

To help the integrator delivering these resources through their chosen web
framework, the helper object ``yafowil.resources.YafowilResources`` should
be used.

The function ``configure_resource_directory`` should be overwritten on deriving
class which is responsible to make the given physical resource directory
somehow available to the web.

The object can be instantiated with ``js_skip`` and ``css_skip`` keyword
arguments, which contain iterable resource group names to skip when calculating
resources. This is useful if basic or dependent resources are already shipped
in another way.

The following example shows how to integrate YAFOWIL resources in a
`pyramid <http://www.pylonsproject.org>`_ application.

.. code-block:: python

    from pyramid.static import static_view
    from yafowil.resources import YafowilResources
    import mypackage.views

    class Resources(YafowilResources):

       def __init__(self, js_skip=[], css_skip=[], config=None):
           self.config = config
           super(Resources, self).__init__(js_skip=js_skip, css_skip=css_skip)

       def configure_resource_directory(self, plugin_name, resourc_edir):
           # instantiate static view
           resources_view = static_view(resourc_edir, use_subpath=True)
           # attach resources view to package
           view_name = '%s_resources' % plugin_name.replace('.', '_')
           setattr(mypackage.views, view_name, resources_view)
           # register view via config
           view_path = 'mypackage.views.%s' % view_name
           resource_base = '++resource++%s' % plugin_name
           self.config.add_view(view_path, name=resource_base)
           return resource_base

    def includeme(config):
        # resources object gets instantiated only once
        resources = Resources(config=config)

        # sorted JS resources URLs. Supposed to be rendered to HTML
        resources.js_resources

        # sorted CSS resources URLs. Supposed to be rendered to HTML
        resources.css_resources
