Elements Explained
==================

Base principles
---------------

YAFOWIL is based on a set of core ideas:

1. Runtime rules, static is subordinate,

2. Don't mess with a framework,

3. Keep it simple and pythonic,

4. No fights with storage,

5. Use chains and trees as structures.

Callables everywhere
--------------------

If you work with YAFOWIL for the first time it probably feels a bit different
compared to other multiple class inheriting, schema based forms.

Instead YAFOWIL uses simple callables at several places. You never need to
inherit any class from yafowil.* (and if you think you need to you don't
understand its architecture and should ask us to improve this documentation).

Callables are used for every extensible aspect of YAFOWIL. They are bundled
as blueprints and used via the factory.

Explanation: Callables are simple functions oder instances of a class with a
``__call__`` method.

Widget
------

A YAFOWIL form consists of a tree of widgets. Everything you would probably
call a "Field" in other form libraries is a widget instance. Widgets can have
children. Thus, also fieldsets and even the form root itself is a widget.

The behavior of a widget is defined by a series of blueprints and properties
as shown below in the referring sections.

The widget class is generic! It's never instanciated directly. The factory is
the only place where this happens.

At creation time of widgets you need to use it's dict-like API for creating
compounds of widgets like a form or a fieldset.

**Attention possible confusion**:

- *Widgets* are build from a chain of blueprints in *existing*
  *libraries/addons*  and are configured using properties,
- *Blueprints* are chains of extractors, renderers, preprocessors and builders
  (see below),
- *average YAFOWIL user* does *not need to create blueprints*, she just use
  them,
- *advanced YAFOWIL users* planning to develop own widgets will need to write
  own blueprints.


Runtime data
------------

While one request to response cycle runs, widgets state is kept in a runtime
data instance. It collects all information like values, request, errors
happened, and the rendered html of a widget in the context of the current
request.


Controller
----------

The controller is responsible for form processing (extraction and validation),
delegation of actions and form rendering (including error handling).

The controller is initialized with a form and request object and immediately
starts the processing. The ``rendered`` instance attribute contains the
rendered form, while the attribute ``data`` contains the extracted runtime data
tree.


Validation
----------

Unlike most form frameworks YAFOWIL does not make a difference between
extraction of a value from the HTTP-request and validation. Both happens in one
processing step. If an extraction step fails it raises a
``yafowil.base.ExtractionError``. This special Python Exception carries a human
readable message and the information if this error shall abort the extraction
chain or not. In either case the form has errors.


Factory
-------

Basics
~~~~~~

The factory knows of the available blueprints and is respsonsible to construct
and configure widget instances. To construct a widget the factory gets called
with the blueprint name as first parameter::

    >>> from yafowil.base import factory
    >>> widget = factory('text', ...)

The behavior of the callbacks in the different execution chains of the
blueprint can be configured with the ``props`` dict. See blueprints reference
for a full list of accepted properties::

    >>> widget = factory('text', props={
    ...     'disabled': 'disabled'})

For the root widget (most probably the form itself), the name attribute must be
given to the factory::

    >>> form = factory('form', name='example_form', props={
    ...     'action': 'http://www.example.com/process_form'})

Child widget names are set transparent using the child ``key``::

    >>> form['field_1'] = factory('text')

Combining blueprints - the factory chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually we have some common widgets, e.g. a pure textarea, and then we need
some label, description, display encountered errors, maybe a table cell or an
encapsulating div and so on. And it can be very different depending on the
framework used or the design we need to implement. But the core functionality
is always the same. In other words: The input field and its behavior is stable,
the eye-candy around it is not.

To solve the different needs, YAFOWIL supports chaining blueprints at factory
time, the so called ``factory chain``.

The blueprint chain is used by passing a colon seperated list of blueprint names
as string to the factory as first argument. I.e. provide a text field inside a
wrapper div with label, help text and error message if extraction failed, call
factory like so::

    >>> form['field_1'] = factory('field:label:error:text', props={
    ...     'label': 'Field 1',
    ...     'help': 'Helptext for field 1',
    ...     'required': 'Field 1 must not be empty'})

This causes the callable chains of each blueprint beeing executed in order.
Extractors are executed from right to left while all others are executed left
to right.

Now we may come up with the problem that several properties refer to more than
one callable inside the execution chains. To address a property specific to a
blueprint of the widget, you can prefix it with the blueprint name.

E.g., 'label.class' addresses the 'class' property of the 'label' blueprint
only instead of effecting all blueprints::

    >>> form['field_1'] = factory('field:label:error:text', props={
    ...     'label': 'Field 1',
    ...     'label.class': 'label_css_class'
    ...     'help': 'Helptext for field 1',
    ...     'required': 'Field 1 must not be empty'})

Macros - predefined factory chains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the lazy people macros are provided. Macros expand to a factory chain of
blueprints. Expansion happens at chain-lookup time before the widget is built.

Macros must be registered in the factory and can override property defaults::

    >>> factory.register_macro('field', 'field:label:error', 'props': {
    ...     'field.class': 'field',
    ...     'field.error_class': 'error',
    ...     'error.class': 'fieldErrorBox',
    ...     'error.render_empty': True,
    ...     'error.position': 'before'})

Now the ``field`` macro can be used inside the factory chain by name prefixed
with ``#``::

    >>> textfield = factory('#field:text')

Custom blueprints
~~~~~~~~~~~~~~~~~

For usecases where it's not worth to write a generic widget for, it's possible
to inject custom blueprints.

Custom blueprints are passed to the factory either as 5-tuple containing chains
of extractors, edit renderers, preprocessors, builders and display renderers,
or as dictionary containing the chains at keys 'extractors', 'edit_renderers',
'preprocessors', 'builders' and 'display_renderers'. Please read the section
about blueprints below to get a deeper understanding of what happens.

Each chain contains callables as explained above. To tell the factory about
usage of a custom blueprint, use the asterisk-prefix in the factory chain,
like::

    ``field:label:*mycustom:textarea``

When using custom blueprints, the factory expects the ``custom``
keyword argument, which is a dict with custom blueprint names as keys
(``mycustom`` in our example), and the custom blueprint configuration as
explained above.

Create custom callbacks::

    >>> def special_renderer(widget, data):
    ...     return u'<SPECIAL>%s</SPECIAL>' % data.rendered

    >>> def special_extractor(widget, data):
    ...     return data.extracted + ['extracted special']

Inject as dict::

    >>> widget = factory('outer:*special:inner', custom={
    ...     'special': {'extractors': [special_extractor], 
    ...                 'edit_renderers': [special_renderer]}})

Inject as list::

    >>> widget = factory('outer:*special:inner', custom={
    ...    'special': ([special_extractor], [special_renderer], [], [], [])})

Custom blueprints are great for easily injecting validation extractors.



Blueprints
----------

Blueprints are a construction guides providing different behaviors on a
widget: i.e. rendering a HTML input field, or extracting and validating input
data or converting data received from the request.

This behaviors are organized as chains of callables. The behavior of the
callables itself is controlled by properties. Each chain has different
responsibilities. Chains are executed left-to-right.

Extractor chain
~~~~~~~~~~~~~~~

Extractors are responsible to get, convert and validate the data of the
current widget in the context of the current request. An extarctor is a
callable expecting a widget instance and a runtime data instance as parameters.

**Userstory**
    An integer field consists of a first extractor getting the value from the
    request paramter matching the widget name. This results in a string.
    Next extractor in chain is responsible to convert the string to an integer.
    If it fails an extraction error is raised. Otherwise the converted value is
    returned. If only positive integers are allowed a validating extractor is
    added to the chain. If its not positive an ExtractionError is raised,
    otherwise the value is returned unmodified.

Edit renderer chain
~~~~~~~~~~~~~~~~~~~

Edit renderers are responsible to create html form output (unicode-strings)
ready to be passed to the response. It is a callable expecting a widget
instance and a runtime data instance as parameters. At this point the runtime
data instance already passed the extraction chain and contains
information about extracted values and errors. Edit renderers may utilize any
templating language if desired. YAFOWIL has no preferences nor does it support
any specific templating language out of the box. All internal rendering in
YAFOWIL happens in pure python.

The edit renderer chain is executed if mode of widget is 'edit'.

**Userstory**
    An file input field has to be rendered with checkboxes to indicate deletion
    of the file. The file input itself is a renderer and the checkboxes are
    another renderer. First renderer in chain creates a pure html ``<input ..>``
    tag for the file upload. Next renderer creates some checkboxes with labels.
    It has access to the string-output of the first renderer as part of
    runtime-data. So some ``<checkbox ..>`` tags can be prepended, wrapped
    around or appended to the previous rendered ``<input ..>``. Both renderers
    are reusable and may be used in other contexts, i.e. in an image blueprint
    context.

Display renderer chain
~~~~~~~~~~~~~~~~~~~~~~

Display renderers are responsible to create html view output (unicode-strings)
ready to be passed to the response.

The display renderer chain is executed if mode of widget is 'display'. Like
edit renderers it is a callable expecting widget and runtime data as parameters
Like the edit renderer it is executed after extraction.

It is possible to mix edit and display renderers in one widget tree, each
widget can have it own mode.

**Userstory**
    A form is created for a complex dataset where different groups of users have
    different access permissions whether to edit or view a dataset value, or
    even to see it at all. The mode property of the widget controlls if the
    rendering chain, and which rendering chain gets executed.

Preprocessor chain
~~~~~~~~~~~~~~~~~~

The preprocessor chain is executed once per request to response cycle
directly after runtime data was created and before extraction happens.
A preprocessor callable can be used to hook up framework specific requirements
and gets widget and runtime data as parameters. There are global preprocessors
running on every widget and widget specific pre-processors. Later are executed
after the global preprocessors.

**Userstory**:
    YAFOWIL expects the request to be a dict like object providing parameters
    via ``get`` and ``__getitem__``. Further i18n support should be available
    i.e. via ``zope.i18n``. A framework integration package now provides one
    global preprocessor function wrapping the request if needed, and another
    hooking up the i18n message factory and the translate function.

Builder chain
~~~~~~~~~~~~~

This chain of callables is called only once right after the widget was created
in the factory. A common use-case is to automatically populate a widget with
child widgets. It expects widget and factory as parameters.

**Userstory**
    A blueprint is written for a complex widget, and luckily there are lots of
    other blueprints already out there providing several behaviors needed.
    If complex blueprint should render i.e. a table containing two fields, a
    builder callable is registered which builds the table containing the 2
    input fields by using the dict like widget API and calling the factory for
    creating it's children.
