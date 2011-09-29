from sphinxext import WidgetDoc, PlanDoc

def setup(app):
    app.add_directive('yafowilwidgets', WidgetDoc)
    app.add_directive('yafowilplans', PlanDoc)