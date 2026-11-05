Encoding of Values
==================

YAFOWIL encodes the values it renders. This page names what it takes care of and
what stays up to the application.


Encoded by YAFOWIL
------------------

- ``Tag`` encodes attribute values: ``&``, ``<``, ``>`` and the delimiting quote.

- The renderers of YAFOWIL and its widgets encode the values they put into text
  content. This includes the value passed to a string ``template``.

Values encoded upfront get encoded twice, so pass them as they are:

.. code-block:: python

    tag = data.tag

    tag('a', tag.escape('a & b'), href='/view?a=1&b=2')
    # <a href="/view?a=1&amp;b=2">a &amp; b</a>

    tag('a', 'a &amp; b', href='/view?a=1&amp;b=2')
    # <a href="/view?a=1&amp;amp;b=2">a &amp; b</a>


Not Encoded
-----------

``label``, ``help``, ``tag.text``, a callable ``template`` and the keys of ``data``
are written by the developer and may contain markup on purpose. Never fill them
from user input.


Custom Renderers
----------------

Inner content passed to ``Tag`` stays as it is, it might be rendered markup. A
renderer encodes values with ``tag.escape``, which also translates them:

.. code-block:: python

    from yafowil.common import fetch_value

    def my_renderer(widget, data):
        tag = data.tag
        value = fetch_value(widget, data)
        return tag('div', tag.escape(value), class_='wrapper')


Rich Text
---------

``yafowil.widget.tiptap`` reduces the value in display mode to what the editor
produces, the property ``sanitizer`` takes a callable to use instead. Templates
rendering the value themselves, e.g. with ``structure``, need to do the same:

.. code-block:: python

    from yafowil.widget.tiptap.sanitizer import sanitize

    html = sanitize(value)

The deprecated ``yafowil.widget.richtext`` and ``yafowil.widget.wysihtml5`` encode
the value in display mode, markup shows up as text.


Content Security Policy
-----------------------

YAFOWIL sends no ``Content-Security-Policy`` header, this is up to the web server
or proxy delivering the application. The header limits what a value can do which
got rendered without encoding by mistake. A starting point:

.. code-block:: text

    default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:

Send it as ``Content-Security-Policy-Report-Only`` first to see what gets refused.
Widgets may need more, e.g. ``yafowil.widget.location`` loads map tiles and queries
a search service on other hosts.
