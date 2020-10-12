from docutils.writers.html4css1 import HTMLTranslator

from yafowil.documentation.sphinxext import PlanDoc, WidgetDoc


# Patch ``HTMLTranslator.visit_container`` to avoid rendering ``container``
# CSS class on div's to avoid messing up bootstrap theme.
def visit_container(self, node):
    # set ``cont`` CSS class instead of ``container``
    self.body.append(self.starttag(node, "div", CLASS="cont"))


HTMLTranslator.visit_container = visit_container


def setup(app):
    app.add_directive("yafowilwidgets", WidgetDoc)
    app.add_directive("yafowilplans", PlanDoc)
