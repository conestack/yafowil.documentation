Elements Explained
==================

Base principles
---------------

YAFOWIL is based on a set of core ideas:

1. Runtime rules, static is subordinate,
2. Don't mess with a framework,
3. Keep it simple and Pythonic,
4. No fights with storage,
5. Use chains and trees as structures.

Callables everywhere
--------------------

If you work with YAFOWIL for the first time, it probably feels a bit different
compared to other multiple-class-inheriting, schema-based forms.

Instead YAFOWIL uses simple callables at several places. You never need to
inherit any class from ``yafowil.*`` (and if you think you need to you don't
understand its architecture and should ask us to improve this documentation).

Callables are used for every extensible aspect of YAFOWIL. They are bundled
as blueprints and used via the factory.

Explanation: Callables are simple functions or instances of a class with a
``__call__`` method.

Widget
------

A YAFOWIL form consists of a tree of widgets. Everything you would probably
call a "Field" in other form libraries is a widget instance. Widgets can have
children. Thus, fieldsets and even the form root itself are also widgets.

The behavior of a widget is defined by a series of blueprints and properties
as shown below in the referring sections.

The widget class is generic! It's never instantiated directly. The factory is
the only place where this happens.

At creation time of widgets you need to use its dict-like API for creating
compounds of widgets, such as a form or a fieldset.

**Attention! Possible confusion:**:

- *Widgets* are built from a chain of blueprints in *existing*
  *libraries/addons* and are configured using properties,
- *Blueprints* are chains of extractors, renderers, preprocessors and builders
  (see below),
- the *average YAFOWIL user* does *not need to create blueprints*, she just uses
  them,
- *advanced YAFOWIL users* planning to develop their own widgets will need to
  write blueprints.


Runtime data
------------

While one request-to-response cycle runs, widgets state is kept in a 
runtime-data instance. It collects all information such as values, request, 
any errors that occurred, and the rendered HTML of a widget in the context of
the current request.


Controller
----------

The controller is responsible for form processing (extraction and validation),
delegation of actions and form rendering (including error handling).

The controller is initialized with a form and request object and immediately
starts the processing. The ``rendered`` instance attribute contains the
rendered form, while the ``data`` attribute contains the extracted runtime-data
tree.


Validation
----------

Unlike most form frameworks, YAFOWIL does not make a distinction between
extraction of a value from the HTTP-request and validation. Both happen in one
processing step. If an extraction step fails, it raises a
``yafowil.base.ExtractionError``. This special Python Exception carries a 
human-readable message and specifies whether this error shall abort the extraction
chain or not. In either case the form has errors.


Factory
-------

Basics
~~~~~~

The factory knows of the available blueprints and is responsible to construct
and configure widget instances. To construct a widget the factory gets called
with the blueprint name as first parameter:

.. code-block:: python

    from yafowil.base import factory
    widget = factory('text', ...)

The behavior of the callbacks in the different execution chains of the
blueprint can be configured with the ``props`` dict. See the blueprints reference
for a full list of accepted properties:

.. code-block:: python

    widget = factory('text', props={
        'disabled': 'disabled',
    })

For the root widget (most probably the form itself), the name attribute must be
given to the factory:

.. code-block:: python

    form = factory('form', name='example_form', props={
        'action': 'http://www.example.com/process_form',
    })

Child widget names are set automatically using the child ``key``:

.. code-block:: python

    form['field_1'] = factory('text')


Combining blueprints - the factory chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usually we have some common widgets, e.g. a pure textarea, and then we need
some label, description, a way to display errors, maybe a table cell or an
encapsulating ``div`` and so on. And it can be very different depending on the
framework used or the design we need to implement. But the core functionality
is always the same. In other words: The input field and its behavior is stable,
the eye-candy around it is not.

To solve the different needs, YAFOWIL supports chaining blueprints at factory
time, the so called ``factory chain``.

The blueprint chain is used by passing a colon-separated list of blueprint names
as a string to the factory as first argument. I.e. to provide a text field inside a
wrapper ``div`` with label, help-text and error message if extraction failed, call
the factory like so:

.. code-block:: python

    form['field_1'] = factory('field:label:error:text', props={
        'label': 'Field 1',
        'help': 'Helptext for field 1',
        'required': 'Field 1 must not be empty',
    })

This causes the callable chains of each blueprint to be executed in order.
Extractors are executed from right to left while all others are executed left
to right.

Now we may come up with the problem that several properties refer to more than
one callable inside the execution chains. To address a property specific to a
blueprint of the widget, you can prefix it with the blueprint name.

E.g., ``label.class`` addresses the ``class`` property of the ``label`` blueprint
only instead of affecting all blueprints:

.. code-block:: python

    form['field_1'] = factory('field:label:error:text', props={
        'label': 'Field 1',
        'label.class': 'label_css_class'
        'help': 'Helptext for field 1',
        'required': 'Field 1 must not be empty',
    })


Macros - predefined factory chains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the lazy people, macros are provided. Macros expand to a factory chain of
blueprints. Expansion happens at chain-lookup time before the widget is built.

Macros must be registered in the factory and can override property defaults:

.. code-block:: python

    factory.register_macro('errorfield', 'field:label:error', 'props': {
        'field.class': 'field',
        'field.error_class': 'error',
        'error.class': 'fieldErrorBox',
        'error.render_empty': True,
        'error.position': 'before',
    })

Now the ``errorfield`` macro can be used inside the factory chain by using the
name prefixed with ``#``:

.. code-block:: python

    textfield = factory('#errorfield:text')


Custom blueprints
~~~~~~~~~~~~~~~~~

For usecases where it's not worth writing a generic widget, it's possible
to inject custom blueprints.

Custom blueprints are passed to the factory either as 5-tuple containing chains
of extractors, edit renderers, preprocessors, builders and display renderers,
or as dictionary containing the chains under the keys ``extractors``,
``edit_renderers``, ``preprocessors``, ``builders`` and ``display_renderers``.
Please read the section about blueprints below to get a deeper understanding of
what happens.

Each chain contains callables as explained above. To tell the factory about
usage of a custom blueprint, use the asterisk-prefix in the factory chain,
as follows::

    ``field:label:*mycustom:textarea``

When using custom blueprints, the factory expects the ``custom``
keyword argument, which is a dict with custom blueprint names as keys
(``mycustom`` in our example), and the custom blueprint configuration as
explained above.

Create custom callbacks:

.. code-block:: python

    def special_renderer(widget, data):
        return u'<SPECIAL>%s</SPECIAL>' % data.rendered

    def special_extractor(widget, data):
        return data.extracted + ['extracted special']

Inject as dict:

.. code-block:: python

    widget = factory('outer:*special:inner', custom={
        'special': {
            'extractors': [special_extractor], 
            'edit_renderers': [special_renderer],
        },
    })

Inject as list:

.. code-block:: python

    widget = factory('outer:*special:inner', custom={
        'special': ([special_extractor], [special_renderer], [], [], []),
    })

Custom blueprints are great for easily injecting validation extractors.


Blueprints
----------

Blueprints are construction guides providing different behaviors on a
widget: e.g. rendering an HTML input field, or extracting and validating input
data or converting data received from the request.

These behaviors are organized as chains of callables. The behavior of the
callables themselves is controlled by properties. Each chain has different
responsibilities. Chains are executed left-to-right.


Extractor chain
~~~~~~~~~~~~~~~

Extractors are responsible to get, convert and validate the data of the
current widget in the context of the current request. An extractor is a
callable expecting a widget instance and a runtime-data instance as parameters.

**User story**
    An integer field consists of:
    - a first extractor getting the value from the request parameter matching
      the widget name. This results in a string.
    - The next extractor in the chain is responsible for converting the string
      to an integer. If it fails, an ``ExtractionError`` is raised. Otherwise the
      converted value is returned.
    - If only positive integers are allowed, a validating extractor is added to
      the chain. If it's not positive, an ``ExtractionError`` is raised, otherwise
      the value is returned unmodified.


Edit renderer chain
~~~~~~~~~~~~~~~~~~~

Edit renderers are responsible to create HTML form output (unicode-strings)
ready to be passed to the response. It is a callable expecting a widget
instance and a runtime-data instance as parameters. At this point the 
runtime-data instance has already passed the extraction chain and contains
information about extracted values and errors. Edit renderers may utilize any
templating language if desired. YAFOWIL has no preferences nor does it support
any specific templating language out of the box. All internal rendering in
YAFOWIL happens in pure Python.

The edit renderer chain is executed if the mode of the widget is ``edit``.

**User story**
    An file input field has to be rendered with checkboxes to indicate whether 
    the file should be deleted.
    The file input itself is a renderer, and the checkboxes are another renderer.
    - The first renderer in chain creates a pure HTML ``<input ..>`` tag for
      the file upload.
    - The next renderer creates some checkboxes with labels. It has access to
      the string output of the first renderer as part of runtime-data. So some
      ``<checkbox ..>`` tags can be prepended, wrapped around or appended to
      the previously rendered ``<input ..>``.
    Both renderers are reusable and may be used in other contexts, e.g. in an
    image blueprint context.


Display renderer chain
~~~~~~~~~~~~~~~~~~~~~~

Display renderers are responsible to create HTML view output (unicode-strings)
ready to be passed to the response.

The display renderer chain is executed if the mode of the widget is ``display``.
Like edit renderers it is a callable expecting widget and runtime-data as
parameters. Like the edit renderer it is executed after extraction.

It is possible to mix edit and display renderers in one widget tree. Each
widget can have its own mode.

**User story**
    A form is created for a complex dataset where different groups of users have
    different access permissions whether to edit or view a dataset value, or
    even to see it at all. The mode property of the widget controls which 
    rendering chain, if any, gets executed.


Preprocessor chain
~~~~~~~~~~~~~~~~~~

The preprocessor chain is executed once per request-to-response cycle,
directly after runtime-data was created and before extraction happens.
A preprocessor callable can be used to hook up framework-specific requirements,
and gets widget and runtime-data as parameters. There are global preprocessors
running on every widget and widget-specific pre-processors. 
Widget-specific pre-processors are executed *after* the global preprocessors.

**User story**:
    YAFOWIL expects the request to be a dict-like object providing parameters
    via ``get`` and ``__getitem__``. Further i18n support should be available
    e.g. via ``zope.i18n``. A framework integration package now provides one
    global preprocessor function wrapping the request if needed, and another
    hooking up the i18n message factory and the translate function.


Builder chain
~~~~~~~~~~~~~

This chain of callables is called only once right after the widget was created
by the factory. A common use-case is to automatically populate a widget with
child widgets. It expects widget and factory as parameters.

**User story**
    A blueprint is written for a complex widget, and luckily there are lots of
    other blueprints already out there providing several behaviors needed.
    If a complex blueprint should render e.g. a table containing two fields, a
    *builder* callable is registered which builds the table containing the 2
    input fields by using the dict-like widget API and calling the factory for
    creating its children.
