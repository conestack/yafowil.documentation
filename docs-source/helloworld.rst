==========================================
Minimal Hello World Example Webapplication
==========================================

This buildout uses ``WebOb`` to help creating a minimal WSGI
application.

Create a minimal filesystem structure::

    cd /PATH/TO/EXAMPLE
    mkdir --parents src/helloworld
    touch src/helloworld/__init__.py
    wget http://python-distribute.org/bootstrap.py
     
Add file ``buildout.cfg`` containing::     

    [buildout]
    parts = helloworld
    develop = .    
    
    [helloworld]
    recipe = zc.recipe.egg:scripts
    egg = helloworld
    
Add file ``setup.py``:

.. code-block:: python

    from setuptools import setup, find_packages
    setup(name='helloworld',
          packages=find_packages('src'),
          package_dir = {'': 'src'},
          install_requires=['setuptools', 'yafowil.webob'],
          entry_points = """\
          [console_scripts]      
          helloworld = helloworld.run:run    
          """ 
    )    

Add ``src/helloworld/run.py`` including a minimal web application, the YAFOWIL
form and a dumb filesystem based storage:

.. code-block:: python

    from yafowil import loader
    import yafowil.webob
    from yafowil.base import factory
    from yafowil.controller import Controller
    from webob import Request, Response

    address, port = '127.0.0.1', 8080 
    url = 'http://%s:%s/' % (address, port)

    def store(widget, data):
        with open('helloworld.txt', 'a') as storage:
            storage.write(data.fetch('helloworld.hello').extracted + '\n')    

    def readall():
        try:
            with open('helloworld.txt', 'r') as storage:
                return reversed(storage.readlines())
        except IOError:
            return ['Empty storage!']

    def next(request):
        return url

    def application(environ, start_response):
        request = Request(environ)
        response = Response()
        response.write('<html><body><h1>YAFOWIL Demo</h1>')
        form = factory(u'form', name='helloworld', props={
            'action': url})
        form['hello'] = factory('field:label:error:text', props={
            'label': 'Enter some text',
            'value': '',
            'required': True})
        form['submit'] = factory('field:submit', props={        
            'label': 'store value',
            'action': 'save',
            'handler': store,
            'next': next})
        controller = Controller(form, request)
        response.write(controller.rendered)
        response.write('<hr />%s</html></body>' % '<br />'.join(readall()))
        return response(environ, start_response)

    def run():
        from wsgiref.simple_server import make_server
        server = make_server(address, port, application)
        server.serve_forever()        

Now bootstrap and run buildout, and start the application.::

    python2.6 bootstrap.py
    ./bin/buildout
    ./bin/helloworld

Pointing the browser to `<http://localhost:8080/>`_ shows the application.

The `full working example code  <https://github.com/bluedynamics/yafowil-example-helloworld>`_
is at github available.
