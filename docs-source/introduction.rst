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

Integration packages such as `yafowil.zope2
<http://pypi.python.org/pypi/yafowil.zope2>`_ or `yafowil.webob
<https://pypi.python.org/pypi/yafowil.webob>`_ are providing
necessary hooks to specific frameworks.


Example
=======

For the impatient, code says more than 1000 words: A very simple example form
works like so::

    >>> import yafowil.loader
    >>> from yafowil.base import factory
    >>> from yafowil.controller import Controller

Create a form.::

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

and some more.

There are also a bunch of add-ons available, usally in the namespace
``yafowil.widget.*``.


Create a widget
===============

Request factory creating a widget instance. I.e. by calling:: 

    >>> widget = factory('text')

where ``text`` is the blueprint registration name.::

    >>> widget = factory('field:label:text')

This causes the widget to use the registered renderers, extractors, etc of the
blueprints ``field``, ``label`` and ``text`` in order.

For convience blueprints can be organised in plans. I.e.::

    >>> widget = factory('#stringfield')
    
expands to ``field:label:widget:text``. See chapter plans for details.


Organize widgets in a tree
==========================

Forms, fieldsets and other compounds are organized as a tree of widgets.
Thus, a widget is either a compound (containing children) or a leaf widget.
For building this trees, the dict like API is used.::

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

You can inject custom behaviour by marking a part of the widget name chain with
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

Invariants are implemented as extractions on compounds. Usally they are put as
custom blueprints with only one extractor on the ``form`` root element itself.

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

    
Add own blueprints
==================

If behaviour (rendering, extracting, etc...) is more general and you need it
more than once you can register it as blueprint in the factory::

    >>> factory.register(
    ...     'myblueprint', 
    ...     extractors=[myvalidator], 
    ...     edit_renderers=[],
    ...     display_renderers=[],
    ...     preprocessors=[],
    ...     builders=[])

and use it now as blueprint when calling the factory::

    >>> widget = factory(
    ...     'field:label:myblueprint:text',
    ...     props={
    ...         'label': 'Inner Field',
    ...     },
    ... )


Using Plans
===========

Plans are a named sets of blueprints. Plans are an abbreviation or shortcuts
to build commonly used combinations of blueprints using the factory.

To indicate a plan the prefix ``#`` is used. I.e. ``#stringfield`` is
registered as a plan and expands to ``field:label:error:text``.

Plans can be combined with other registered blueprints and custom blueprints
too, i.e. ``*myvalidatingextractor:#numberfieldfield`` expands to
``*myvalidatingextractor:field:label:error:text``.

It is possible to register own plans to the factory, like so::

    >>> from yafowil.base import factory
    >>> factory.register_plan(
    ...     'divstringfield',
    ...     'field:label:error:div:text')
    >>> mywidget = factory('#divstringfield')

Its also possible to overwrite already registered plans.