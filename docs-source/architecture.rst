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
compared to other multiple class inheriting, schema based forms. Instead YAFOWIL 
uses simple callables at several places. You never need to inherit any class
from yafowil.* (and if you think you need to you don't understand its 
architecture).

Callables are used for every extensible aspect of YAFOWIL. They are bundled
as blueprints and used via the factory.

Explanation: Callables are simple functions oder instances of a class with a ``__call__`` method.

Widget
------

A YAFOWIL form consists of a tree of widgets. Everything you would probably
call a "Field" in other form libraries is a widget instance. Widgets can have
children. Thus, also fieldsets and even the form root itself is a widget.

The behavior of a widget is defined by blueprints and properties as shown below
in the referring sections.

The widget class is generic:

- It's never instanciated directly. The factory is the only place where this
  happens.
- Except some rare cases you never touch it further. The controller does the
  handling.

At creation time of widgets you need to use it's dict-like API for creating
compounds of widgets like a form or a fieldset.

Runtime data
------------

While one cycle runs (request to response), the state of the widget is kept in
a runtime data object. It collects all information like values, request, errors
happened, and the rendered html of a widget in the context of the current
request.

Blueprint
---------

A blueprint is a construction guide for providing different behaviors on a
widget, like rendering a HTML input field, or extracting, validating or
converting data received from the request.

This behaviors are organized as chains of callables. The behavior of the
callables itself is controlled by the properties passed to the factory. Each
chain has different responsibilities. Chains are executed left-to-right.

Extractor chain
~~~~~~~~~~~~~~~

An extractor is responsible to get, convert and validate the data of the
current widget in the context of the request. It is a callable expecting the
widget instance and the runtime data (holding the request, errors and values)
as parameters.

**Userstory**
    An Integer Field consists of the pure extractor which results in a string.
    Next extractor in the chain is responsible to convert it to an integer.
    If it fails an extraction error is raised, otherwise the converted value is
    returned. If only positive integers are allowed we can add a validating
    extractor to the chain and so on.

Edit renderer chain
~~~~~~~~~~~~~~~~~~~

The edit_renderer is responsible to create form output (text, unicode)
ready to be passed to the response. It is a callable expecting the widget
instance and runtime data (after extraction chain has been executed) as
parameters. It can utilize any templating language if desired. YAFOWIL has no
preferences nor does it support any specific templating language out of the
box. All internal rendering in YAFOWIL happens in pure python.

The edit renderer chain is executed if mode of widget is 'edit'.

**Userstory**
    A simple HTML text input field should be rendered with a referring label,
    an error if happened at extraction time and a wrapper element with some
    CSS class set. The downstream renderer in the chain can access the
    rendered output of the preceding and so on. Thus a pure html ``<input ..>``
    markup rendered by one callable can be wrapped with a label rendered by
    another callable, and so on.

Preprocessor chain
~~~~~~~~~~~~~~~~~~

The preprocessor chain is executed once per cycle (request to response)
directly after runtime data was created. A preprocessor callable can be used to
hook up framework specific requirements and gets widget and runtime data as
parameters.

**Userstory**:
    YAFOWIL expects the request to be a dict like object providing parameters
    via ``get`` and ``__getitem__``. Further i18n support should be available
    via ``zope.i18n``. A framework integration package now provides one
    preprocessor function wrapping the request if needed, and another hooking
    up the i18n message factory and the translate function.

Builder chain
~~~~~~~~~~~~~

A builder is a callable responsible to automatically populate a widget
with child widgets. It expects the widget and the factory itself as
parameters. The builder chain is executed at at the time when the factory is
called to produce a widget right after the parent widget is created and
configured.

**Userstory**
    A blueprint is written for a complex widget, and luckily there are lots of
    other blueprints already out there providing several behaviors needed.
    If complex blueprint should render i.e. a table containing two fields, a
    builder callable is registered which builds the table containing the 2
    input fields by using the dict like widget API and calling the factory for
    creating it's children.

Display renderer chain
~~~~~~~~~~~~~~~~~~~~~~

The display_renderer is responsible to create view output (text, unicode)
ready to be passed to the response.

The display renderer chain is executed if mode of widget is 'display'. Like
edit_renderer, it is a callable expecting the widget instance and runtime data
(after extraction chain has been executed) as parameters.

**Userstory**
    A form is created for a complex dataset where different groups of users have
    different access permissions whether to edit or view a dataset value, or
    even to see it at all. The mode property of the widget controlls if the
    rendering chain, and which rendering chain gets executed.

Factory basics
--------------

The factory knows of the available blueprints and is used to construct the
widget instances. To construct a widget the factory gets called with the
blueprint name as first parameter::

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
----------------------------------------

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
----------------------------------

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
-----------------

For usecases where it's not worth to write a generic widget for, it's possible
to inject custom blueprints.

Custom blueprints are passed to the factory either as 5-tuple containing chains
of extractors, edit renderers, preprocessors, builders and display renderers,
or as dictionary containing the chains at keys 'extractors', 'edit_renderers',
'preprocessors', 'builders' and 'display_renderers'.

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
extraction of a value from the HTTP-request and validation. both happens in one
chain. If an extraction step fails it raises a ``yafowil.base.ExtractionError``.
This special Python Exception carries a human readable message and the
information if this error shall abort the extraction chain or not. In either
case the form has errors.
