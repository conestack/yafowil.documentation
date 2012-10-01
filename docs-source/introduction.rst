============
Introduction
============

YAFOWIL targets rendering form widgets and extracting/validating the data send
by the browser per widget.

YAFOWIL widgets are just configuration. It provides a factory which can
produce widget instances from blueprints, or blueprints can be registered.

Motivation
==========

Tired of inventing widgets again and again after switching the Python framework
YAFOWIL is intentionally written framework-independent. By just feeding it with
configuration it can be used and extended in most of existing python web
frameworks. Zope, Pyramid, Django and Flask are hot candidates.

Another common problem with form libs is a non-unique look and feel of the
available widget collection. YAFOWIL tries to provide some useful addon widgets
which tries to take care of a unified user experience.

Dependencies
============

YAFOWIL aims to have no dependencies to any web framework. It utilizes the
`node <http://pypi.python.org/pypi/node>`_
package. YAFOWIL does not know about data-storage, but offers a hook to add
processing callback handler function.

Integrations
============

Framework integration packages:

* `yafowil.plone <http://pypi.python.org/pypi/yafowil.plone>`_
* `yafowil.webob <http://pypi.python.org/pypi/yafowil.webob>`_
* `yafowil.werkzeug <http://pypi.python.org/pypi/yafowil.werkzeug>`_
* `yafowil.bootstrap <http://pypi.python.org/pypi/yafowil.werkzeug>`_

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

Provided blueprints
===================

YAFOWIL provides blueprints for all HTML standard inputs, lots of helper
blueprints for buidling complex widgets and a bunch of add-ons available,
usally in the namespace ``yafowil.widget.*``.

See blueprints reference to get a complete overview of blueprints.

Produce a widget
================

Yafowil uses a factory for creating widget instances. I.e. by calling:: 

    >>> widget = factory('text')

a text input widget is produced from blueprint ``text``.

Blueprints can be chained by colon separated names or given as list::

    >>> widget = factory('field:label:text')

This causes the created widget to use the registered renderers, extractors,
etc of the blueprints ``field``, ``label`` and ``text`` in order.

Blueprint chains can be organised as plans. I.e.::

    >>> widget = factory('#stringfield')
    
expands to ``field:label:widget:text``. See chapter plans for details.

Organize widgets in a tree
==========================

Forms, fieldsets and other compounds are organized as a tree of widgets.
Thus, a widget is either a compound node (containing children) or a leaf node
in this tree.

For building widget trees, the dict like API is used.::

    >>> form = factory('form', 'UNIQUENAME', props={
    ...     'action': 'someurl'})
    >>> form['somefield'] = factory('field:label:text', props={
    ...     'label': 'Some Field'})
    >>> form['somefieldset'] = factory('fieldset', props={
    ...     'legend': 'A Fieldset'})
    >>> form['somefieldset']['innerfield'] = factory('field:label:text', props={
    ...     'label': 'Inner Field'})

Add custom behaviour
====================

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
    ...    return data.extracted
         
    >>> widget = factory('field:label:*myvalidation:text', props={
    ...     'label': 'Inner Field'},
    ...     custom: {
    ...         'myvalidation': ([myvalidator],[],[],[],[])})

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
    ...         error = ExtractionError(
    ...             'provide hello or world, not both or none')
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

If a behaviour (rendering, extracting, etc...) is more general and needed
more than once, it can be registered as blueprint in the factory::

    >>> factory.register(
    ...     'myblueprint', 
    ...     extractors=[myvalidator], 
    ...     edit_renderers=[],
    ...     display_renderers=[],
    ...     preprocessors=[],
    ...     builders=[])

and then uses as regular blueprint when calling the factory::

    >>> widget = factory('field:label:myblueprint:text', props={
    ...     'label': 'Inner Field'})

Using Macros
============

Macros are a named chains of blueprints. Macros are an abbreviation or shortcuts
to build commonly used combinations of blueprints using the factory.

To indicate a plan the prefix ``#`` is used. I.e. ``#field`` is
registered as a plan and expands to ``field:label:error``.

Macros can be combined with other macros, blueprints or custom
blueprints, i.e. ``#field:*myvalidatingextractor:textarea`` expands to
``field:label:error:*myvalidatingextractor:text``.

It is possible to register own macros in the factory::

    >>> from yafowil.base import factory
    >>> factory.register_macro(
    ...     'myfield',
    ...     'field:label:error:div')
    >>> mywidget = factory('#myfield')

Its also possible to overwrite already registered macros.
