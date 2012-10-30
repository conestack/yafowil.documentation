============
Introduction
============

YAFOWIL targets rendering form widgets and extracting/validating the data send
by the browser per widget.

YAFOWIL widgets are just configuration. It provides a factory which can
produce widget instances from blueprints.

There is a library of existing blueprints ready to be extended on demand.

YAFOWIL provides blueprints for all HTML standard inputs, lots of helper
blueprints for buidling complex widgets and a bunch of add-ons (usally in
namespace ``yafowil.widget.*``).

Motivation
==========

Tired of inventing widgets again and again after switching the Python framework
YAFOWIL is intentionally written framework-independent. By just feeding it with
configuration it can be used and extended in most of existing python web
frameworks. Zope, Pyramid, Django, Flask, CherryPy and similar are
candidates.

Another common problem with form libs is a non-unique look and feel of the
available widget collection. YAFOWIL tries to provide some useful addon widgets
which tries to take care of a unified user experience.

Dependencies
============

YAFOWIL aims to have no dependencies to any web framework. It utilizes the
`node <http://pypi.python.org/pypi/node>`_
package. YAFOWIL does not know about data-storage, but offers a hook to add
processing callback handler functions.

Integrations
============

YAFOWIL currently integrates with the following packages:

* `yafowil.plone <http://pypi.python.org/pypi/yafowil.plone>`_
* `yafowil.webob <http://pypi.python.org/pypi/yafowil.webob>`_
* `yafowil.werkzeug <http://pypi.python.org/pypi/yafowil.werkzeug>`_
* `yafowil.bootstrap <http://pypi.python.org/pypi/yafowil.werkzeug>`_

For details read the chapter ``integrations``.

Example
=======

For the impatient, code says more than 1000 words: A simple example form works
like so::

    >>> import yafowil.loader
    >>> from yafowil.base import factory
    >>> from yafowil.controller import Controller

Produce a form.::

    >>> form = factory('form', name='myform', props={
    ...     'action': 'http://www.domain.tld/someform'})
    
    >>> form['someinput'] = factory('label:text', props={
    ...     'label': 'Your Text'})

    >>> def formaction(widget, data):
    ...     data.printtree()

    >>> def formnext(request):
    ...     return 'http://www.domain.tld/result'

    >>> form['submit'] = factory('submit', props={
    ...     'handler': formaction,
    ...     'next': formnext,
    ...     'action': True})

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

Get form data from of request (request is expected dict-like)::

    >>> request = {'myform.someinput': 'Hello World',
    ...            'action.myform.submit': 'submit'}
    >>> controller = Controller(form, request)
    >>> controller.data
    <RuntimeData myform, value=None, extracted=None at ...>
      <RuntimeData myform.someinput, value=None, extracted='Hello World',
      attrs={'input_field_type': 'text'} at ...>
      <RuntimeData myform.submit, value=None, extracted=<UNSET> at ...>

Creating a widget
=================

A widget is an instance of a blueprint created by the factory. Factory is a
singleton and operates also as a registry for blueprints.

By calling the factory a widget is created, here a naked text input field from
the blueprint ``text``:: 

    >>> widget = factory('text')

Blueprints can be chained by colon separated names or given as list::

    >>> widget = factory('field:label:text')

This causes the created widget to chain the registered renderers, extractors,
and other parts of the blueprints ``field``, ``label`` and ``text`` in order.

Blueprint chains can be organised using as macros to reduce the complexity of
factory calls (details below). I.e.::

    >>> widget = factory('#field:text')
    
expands the macro ``#field`` to ``field:label:error`` and appends ``:text`` so
the result is ``field:label:error:text``.


Widgets are Organized as a Tree
===============================

Any HTML form can be visualized as a tree: The ``<form>`` is the root,
``<input>`` elements are its children. Also a ``<fieldset>`` grouping a bunch of
``<input>`` is a compound with children. In YAFOWIL the form is organized as a
tree which is like a ordered python ``dict`` with each value a dict again. Widget
instances are ``dict-like`` objects.

Thus, a widget is either a compound node (containing children) or a leaf node
in this tree.

Building widget trees is as simple as using python dicts::

    >>> form = factory('form', 'UNIQUENAME', props={
    ...     'action': 'someurl'})
    >>> form['somefield'] = factory('field:label:text', props={
    ...     'label': 'Some Field'})
    >>> form['somefieldset'] = factory('fieldset', props={
    ...     'legend': 'A Fieldset'})
    >>> form['somefieldset']['innerfield'] = factory('field:label:text', props={
    ...     'label': 'Inner Field'})

Rendering Mode
==============

The way a widget is rendered is controlled by the mode. Every widget may given
a ``mode`` keyword argument to the factory as a string or a callable accepting
two parameters  ``widget`` and ``data``returning a string.

These modes are supported:

``edit``
    Default classic mode, editing of form is possible. Rendering follows the
    registered ``edit_renderers``.

``display``
    No form elements are rendered, just the data as defined by registerd
    ``display_renders``.

``skip``
    Renders just an empty string.


Validation
==========

In YAFOWIL validation and extraction happens at the same time. Extraction means
to get a meaningful value out of the request. Validation means to check
constraints, i.e if a number is positive or an e-mail-adress is valid.

Invariants
==========

Invariants are implemented as extractors on compounds. Usally they are put as
a custom blueprint (see below) with one extractor on some parent of the elements
to validate.

Here is a short example (extension of the ``hello world`` example) for a custom
invariant extractor which checks if one or the other field is filled, but never
both or none (XOR)::

    >>> from yafowil.base import ExtractionError
    >>> # ... see helloworld example whats missing here
    
    >>> def myinvariant_extractor(widget, data):
    ...     if not (bool(data['hello']) != bool(data['world']):
    ...         error = ExtractionError(
    ...             'provide hello or world, not both or none')
    ...         data['hello'].error.append(error)
    ...         data['world'].error.append(error)
    ...     return data.extracted
    
    >>> def application(environ, start_response): 
    ...     # ... see helloworld example whats missing here
    ...     form = factory(u'*myinvariant:form', name='helloworld', 
    ...         props={'action': url},
    ...         custom={'myinvariant': dict(extractors=[myinvariant_extractor])}
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

General behaviours (rendering, extracting, etc...) can be registered as
blueprint in the factory::

    >>> factory.register(
    ...     'myblueprint', 
    ...     extractors=[myvalidator], 
    ...     edit_renderers=[],
    ...     display_renderers=[],
    ...     preprocessors=[],
    ...     builders=[])

and then used as regular blueprint when calling the factory::

    >>> widget = factory('field:label:myblueprint:text', props={
    ...     'label': 'Inner Field'})


Adding custom behaviour
=======================

It's possible to inject custom behaviour by marking a part of the blueprint
chain with the asterisk ``*`` character. Behaviours are one or a combination
of a

``extractor``
    extracts, validates and/or converts form-data from the request.

``edit_renderer``
    build the markup for editing.

``display_renderer``
    build the markup for display only.

``builder``
    Generic hook called once at factory time of the widget. Here i.e. subwidgets
    can be created.

``preprocessor``
    Generic hook to prepare runtime-data. Runs once per runtime-data instance
    before extractors or renderers are running.

::

    >>> def myvalidator(widget, data):
    ...    # validate the data, raise ExtractionError if somethings wrong
    ...    if data.extracted != 'something:'
    ...        raise ExtractionError("only 'something' is allowed as input.")
    ...    return data.extracted
         
    >>> widget = factory('field:label:*myvalidation:text', props={
    ...     'label': 'Inner Field'},
    ...     custom: {
    ...         'myvalidation': dict(extractor=[myvalidator])
    ... )}
