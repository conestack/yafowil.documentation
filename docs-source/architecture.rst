Elements Explained
==================

Base Principles
---------------

YAFOWIL is based on a set of core ideas:

1. Runtime rules, static is subordinate,

2. Don't mess with a framework,

3. Keep it simple and pythonic,

4. No fights with storage,

5. Use chains and trees as structures.

Callables Everywhere
--------------------

If you work with YAFOWIL for the first time it probably feels a bit different 
compared to other multiple class inheriting, schema based forms. Instead YAFOWIL 
uses simple callables at several places. You never need to inherit any class
from yafowil.* (and if you think you need to you don't understand its 
architecture).

Callables are used for every extensible aspect of YAFOWIL. They are bundled
as blueprints and used via the factory.

Widget
------

A widget is a combination of blueprints (see below) and properties.

The widget class is generic:

- You never need to instantiate it directly. The factory is the only place where
  this happens.
- Except some very very rare cases you never touch it further. The controller
  does the handling.

Only at creation time of a widget you need to use its dict-like api. This is the
case if you create compounds of widgets, i.e. a form or a fieldset.

To address a property specific to a blueprint of the widget, you can prefix it
with it's name. E.g. 'label.title' instead of just writing 'title'.

Runtime Data
------------

While one cycle runs (request to response), the state of the widget is kept in
a runtime data object. It collects all information like values, request, errors
happened, and the rendered html of a widget in the context of the current
request.

Blueprint
---------

A blueprint is a part of a widget, e.g. a bare html input field, a bare label
and so on.

A blueprint consists of different chains of callables. Each chain has different
responsibilities. Chains are executed left-to-right.

callable: extractor
    An extractor is responsible to get, convert and validate the data of the
    current widget in the context of the request. It is a callable expecting the
    widget instance and the runtime data (with request, errors and values)
    as parameters.

chain #1: extractors
    Extractors are chained. Example: An Integer Field consists of the
    pure extractor which results in a string. Next extractor in the chain is
    responsible to convert it to an integer. If it fails an error is marked,
    otherwise the value on data is of type ``int``. If only positive
    integers are allowed we can add a validating extractor to the chain.

callable: edit_renderer
    The edit_renderer is responsible to create form output (text, unicode)
    ready to be passed to the response. Edit renderers refer to mode 'edit' of
    widget nodes. It is a callable expecting the widget
    instance and runtime data (after extraction is run) as parameters. It can
    utilize any templating language. YAFOWIL has no preferences nor does it
    support any specific templating language out of the box. All internal
    rendering in YAFOWIL happens in pure python.

chain #2: edit_renderers
    Edit renderers are chained. The second renderer in the chain can access the
    rendered output of the first and so on. Thus a pure html ``<input ..>``
    widget can be wrapped with a label etc.

callable: preprocessor
    A preprocessor can be used in many different ways. It is executed in one
    run (request to response) once direct after runtime data is created. It
    gets widget and runtime data as parameters.

callable: global preprocessor
    A factory global preprocessor executed for every widget produced by the
    factory. It will be executed before all other preprocessors are
    run. It can be used to do framework specific conversions e.g. for the
    request.

chain #3: preprocessors/ global preprocessors
    Preprocessors are chained. The chain of preprocessors is executed once
    after creation of a new runtime data object, i.o.w. once in a run at the
    very beginning of the run.

callable: builder
    A builder is a callable responsible to automatically populate a widget
    with child widgets. It expects the widget and the factory itself as
    parameters. Its a kind of automatic compound and is executed at
    factory time, at the time when the factory is called to produce a widget right
    after the parent widget is created and configured. Its intended use is to
    make it easy to provide groups of widgets which are always the same. E.g.
    a password validation widget consisting of two password input fields.

chain #4: builders
    Builders are chained. The chain is executed one by one at factoring
    time once per widget instance.

callable: display_renderer
    The display_renderer is responsible to create view output (text, unicode)
    ready to be passed to the response.  Display renderers refer to mode
    'display' of widget nodes. Like edit_renderer, it is a callable expecting
    the widget instance and runtime data (after extraction run) as parameters.

chain #5: display_renderers
    Display renderers are chained. The second renderer in the chain can access
    the rendered output of the first and so on.

Factory
-------

The factory contains blueprints - generic plans - for parts of a widget.
It is responsible to create widgets out of a chained combination of blueprints
and add widget specific properties.


Combining Blueprints - Chaining
-------------------------------

Usually we have some common widgets, e.g. a pure textarea, and then we need
some label, description, display encountered errors, maybe a table cell or an
encapsulating div and so on. And it can be very different depending on the
framework used or the design we need to implement. But the core functionality
is always the same. In other words: The input field and its behavior is stable,
the eye-candy around it is not.

This is what the user of YAFOWIL can change with ease. We call this
``factory chain``. At factory time, when the widget is requested from the
factory, additional configurations can be added by passing a colon separated
list of names, like ``label:textarea`` or ``myproject.field:label:textarea``
and so on. Thus we can chain blueprints.

Extractors in these chained blueprints are executed from right to left while all
others are executed left to right.

Plans: Predefined Combined Blueprints
-------------------------------------

For the lazy people plans are provided. Plans are prefixed by ``#`` and expand
to a factory chain of blueprints. Expansion happens at chain-lookup time before
the widget is built.

Custom Blueprint
----------------

In case of use-cases not worth to write a generic widget for, it's possible to
create custom blueprints. Custom blueprints are passed to the factory either as
5-tuple containing chains of extractors, edit renderers, preprocessors, builders
and display renderers, or as dictionary containing the chains at keys
'extractors', 'edit_renderers', 'preprocessors', 'builders' and
'display_renderers'. Each chain contains callables as explained above. To tell
the factory about usage of a custom blueprint, use the asterisk-prefix like
``field:label:*mycustom:textarea`` in the factory chain. Next the factory
takes an keyword-argument ``custom`` expecting a dict with key ``mycustom``
and a custom blueprint as explained above.

**Example:**

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

Custom blueprints are great for easily injecting validating extractors.

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
