=========
Resources
=========

YAFOWIL widgets ship with JavaScript and CSS resources. These are registered
to the factory with delivery order and grouping information.


YafowilResources Helper
=======================

Use ``yafowil.resources.YafowilResources`` to integrate resources with your
web framework:

.. code-block:: python

    from yafowil.resources import YafowilResources

    class Resources(YafowilResources):

        def configure_resource_directory(self, plugin_name, resource_dir):
            # Make resource_dir available via your web framework
            # Return the base URL for the resources
            return f'/static/{plugin_name}'

    resources = Resources()

    # Get sorted resource URLs
    js_urls = resources.js_resources
    css_urls = resources.css_resources


Skipping Resources
==================

Skip resources that are already provided elsewhere:

.. code-block:: python

    resources = Resources(
        js_skip=['jquery', 'bootstrap'],
        css_skip=['bootstrap'],
    )


Pyramid Example
===============

.. code-block:: python

    from pyramid.static import static_view
    from yafowil.resources import YafowilResources

    class Resources(YafowilResources):

        def __init__(self, config, js_skip=[], css_skip=[]):
            self.config = config
            super().__init__(js_skip=js_skip, css_skip=css_skip)

        def configure_resource_directory(self, plugin_name, resource_dir):
            view = static_view(resource_dir, use_subpath=True)
            view_name = f'{plugin_name.replace(".", "_")}_resources'
            resource_base = f'++resource++{plugin_name}'
            self.config.add_view(view, name=resource_base)
            return resource_base

    def includeme(config):
        resources = Resources(config)
        # Use resources.js_resources and resources.css_resources
        # in your templates
