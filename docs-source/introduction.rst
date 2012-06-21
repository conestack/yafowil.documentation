============
Introduction
============

It's all just about rendering widgets and extracting the data returned from the
browser per widget.

YAFOWIL widgets are just configuration. YAFOWIL provides a factory where you can
fetch your widgets instances from. Or you register your own.

Dependencies
============

YAFOWIL aims to have no dependencies to any framework. It utilizes the `node
<http://pypi.python.org/pypi/node>`_
package. It also does not know about data-storage, but offers you a hook to add
your handler.

Tired of inventing widgets again and again after switching the Python framework
YAFOWIL is intentionally written framework-independent. By just feeding it with
configuration it can be used and extended in most of existing python web
frameworks. Zope, Pyramid and Django are hot candidates.

The integration packages `yafowil.plone
<http://pypi.python.org/pypi/yafowil.plone>`_, `yafowil.webob
<http://pypi.python.org/pypi/yafowil.webob>`_ and  `yafowil.werkzeug
<http://pypi.python.org/pypi/yafowil.werkzeug>`_ are providing
necessary hooks to this specific frameworks.


Example
=======

For the impatient, code says more than 1000 words: A very simple example form
works like so::

    >>> import yafowil.loader
    >>> from yafowil.base import factory
    >>> from yafowil.controller import Controller

Produce a form.::

    >>> form = factory(
    ...     'form',
    ...     name='myform',
    ...     props={
    ...         'action': 'http://www.domain.tld/someform',
    ...     }
    ... )
    >>> form['someinput'] = factory(
    ...     'label:text',
    ...     props={
    ...         'label': 'Your Text',
    ...     }
    ... )

    >>> def formaction(widget, data):
    ...     data.printtree()

    >>> def formnext(request):
    ...     return 'http://www.domain.tld/result'

    >>> form['submit'] = factory(
    ...     'submit',
    ...     props={
    ...         'handler': formaction,
    ...         'next': formnext,
    ...         'action': True,
    ...     }
    ... )

Render empty form by calling the form object::

    >>> rendered = form()

This results in::

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

Get form data out of request (request is expected dict-like).::

    >>> request = {
    ...     'myform.someinput': 'Hello World',
    ...     'action.myform.submit': 'submit',
    ... }
    >>> controller = Controller(form, request)
    >>> controller.data
    <RuntimeData myform, value=None, extracted=None at ...>
      <RuntimeData myform.someinput, value=None, extracted='Hello World',
      attrs={'input_field_type': 'text'} at ...>
      <RuntimeData myform.submit, value=None, extracted=<UNSET> at ...>


Basic functions
===============

YAFOWIL provides widgets for all HTML standard inputs, Such as:

- text (inluding email, number, url, ...)
- textarea
- checkbox and radio
- selects (single, multiple)
- file
- hidden
- submit

etc...

There are also a bunch of add-ons available, usally in the namespace
``yafowil.widget.*``.


Produce a widget
================

Yafowil uses a factory for creating widget instances. I.e. by calling:: 

    >>> widget = factory('text')

a text input widget is produced, where ``text`` is the blueprint registration
name.

Blueprints can be chained by colon separated blueprint names or given as list::

    >>> widget = factory('field:label:text')

This causes the created widget to use the registered renderers, extractors,
etc of the blueprints ``field``, ``label`` and ``text`` in order.

Blueprint chains can be organised in so called plans. I.e.::

    >>> widget = factory('#stringfield')
    
expands to ``field:label:widget:text``. See chapter plans for details.


Organize widgets in a tree
==========================

Forms, fieldsets and other compounds are organized as a tree of widgets.
Thus, a widget is either a compound node (containing children) or a leaf node 
in this tree.

For building widget trees, the dict like API is used.::

    >>> form = factory(
    ...     'form',
    ...     'UNIQUENAME',
    ...     props={
    ...         'action': 'someurl',
    ...     },
    ... )
    >>> form['somefield'] = factory(
    ...     'field:label:text',
    ...     props={
    ...         'label': 'Some Field',
    ...     },
    ... )
    >>> form['somefieldset'] = factory(
    ...     'fieldset',
    ...     props={
    ...         'legend': 'A Fieldset',
    ...     },
    ... )
    >>> form['somefieldset']['innerfield'] = factory(
    ...     'field:label:text',
    ...     props={
    ...         'label': 'Inner Field',
    ...     },
    ... )


Add custom behaviour
====================

You can inject custom behaviour by marking a part of the blueprint chain with
the asterisk ``*`` character. Behaviours are one or a combination of a

``extractor``
    extracts, validates and/or converts form-data from the request

``edit_renderer``
    build the markup for editing

``preprocessor``
    Generic hook to prepare runtime-data. Runs once per runtime-data instance
    before extractors or renderers are running.

``builder``
    Generic hook called once at factory time of the widget. Here i.e. subwidgets
    can be created.

``display_renderer``
    build the markup for display only

::

    >>> def myvalidator(widget, data):
    ...    # validate the data, raise ExtractionError if somethings wrong
    ...    return data.extracted
         
    >>> widget = factory(
    ...     'field:label:*myvalidation:text',
    ...     props={
    ...         'label': 'Inner Field',
    ...     },
    ...     custom: {
    ...         'myvalidation': ([myvalidator],[],[],[],[]),
    ...     }
    ... )


Invariants
==========

Invariants are implemented as extractors on compounds. Usally they are put as
custom blueprint with one extractor on some parent of the elements to validate.

Here is a short example (extension of the ``hello world`` example) for a custom
invariant extractor which checks if one or the other field is filled, but never
both or none::

    >>> from yafowil.base import ExtractionError
    >>> # ... see helloworld example whats missing here
    
    >>> def myinvariant_extractor(widget, data):
    ...     if not (bool(data['hello']) != bool(data['world']):
    ...         error = ExtractionError('provide hello or world, not both or none')
    ...         data['hello'].error.append(error)
    ...         data['world'].error.append(error)
    ...     return data.extracted
    
    >>> def application(environ, start_response): 
    ...     # ... see helloworld example whats missing here
    ...     form = factory(u'*myinvariant:form', name='helloworld', 
    ...         props={'action': url},
    ...         custom={'myinvariant': ([myinvariant_extractor], [], [], [], [])
    ...         )
    ...     form['hello'] = factory('field:label:error:text', props={
    ...         'label': 'Enter some text here',
    ...         'value': ''})
    ...     form['world'] = factory('field:label:error:text', props={
    ...         'label': 'OR Enter some text here',
    ...         'value': ''})
    ...     # ... see helloworld example whats missing here

    
Providing blueprints
====================

If behaviour (rendering, extracting, etc...) is more general and you need it
more than once you can register it as blueprint in the factory::

    >>> factory.register(
    ...     'myblueprint', 
    ...     extractors=[myvalidator], 
    ...     edit_renderers=[],
    ...     display_renderers=[],
    ...     preprocessors=[],
    ...     builders=[])

and use it now as regular blueprint when calling the factory::

    >>> widget = factory(
    ...     'field:label:myblueprint:text',
    ...     props={
    ...         'label': 'Inner Field',
    ...     },
    ... )


Using Plans
===========

Plans are a named chains of blueprints. Plans are an abbreviation or shortcuts
to build commonly used combinations of blueprints using the factory.

To indicate a plan the prefix ``#`` is used. I.e. ``#stringfield`` is
registered as a plan and expands to ``field:label:error:text``.

Plans can be combined with other plans, registered blueprints or custom
blueprints, i.e. ``*myvalidatingextractor:#numberfieldfield`` expands to
``*myvalidatingextractor:field:label:error:text``.

It is possible to register own plans to the factory::

    >>> from yafowil.base import factory
    >>> factory.register_plan(
    ...     'divstringfield',
    ...     'field:label:error:div:text')
    >>> mywidget = factory('#divstringfield')

Its also possible to overwrite already registered plans.