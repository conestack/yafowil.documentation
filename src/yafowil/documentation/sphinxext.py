from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.nodes import nested_parse_with_titles

import yafowil.loader
import yafowil.widget.autocomplete
import yafowil.widget.richtext
import yafowil.widget.datetime
import yafowil.widget.dict
import yafowil.widget.dynatree
from yafowil.base import factory

class WidgetDoc(Directive):
    
    def run(self):
        result = []
        for key in sorted(factory._factories.keys()):
            result.append(self._doc_widget(key))
        return result        
    
    def _doc_widget(self, widgetname):
        sec = nodes.section()
        sec['ids'].append(widgetname)
        # set a title:
        sec.append(nodes.subtitle(text=widgetname))
        # fetch main documentation
        maindoc = factory.doc['widget'].get(widgetname, None)        
        if maindoc is not None:            
            sec.append(self._rest2node(maindoc))
        else:
            sec.append(nodes.paragraph(
                text='This widget is currently undocumented.'))
        
        # build table of callables used
        rub = nodes.rubric(text='Chains')
        sec.append(rub)
        table= """
        +------------+-----------+---------------+----------+
        | extractors | renderers | preprocessors | builders |
        +============+===========+===============+==========+
        | replace    | replace   | replace       | replace  |
        +------------+-----------+---------------+----------+
        """   
        table = self._rest2node(table)        
        rub.append(table)
        entries = table.children[0].children[0].children[5].children[0]
        for idx in range(0,4):
            entries[idx].children = []
            entries[idx].append(self._doc_chain(widgetname, idx))      

        # document properties
        rub = nodes.rubric(text='Properties')
        sec.append(rub)
        dl = nodes.definition_list()
        rub.append(dl)
        for prop in sorted([_ for _ in factory.doc['props'] 
                           if _.startswith('%s.' % widgetname)]):
            dl.append(self._doc_property(prop))
                               
        return sec
    
    def _doc_chain(self, widgetname, chainidx):
        ol = nodes.enumerated_list()
        chain = factory._factories[widgetname][chainidx]
        exist = False
        for el in chain:
            exist = True
            li = nodes.list_item()
            if hasattr(el, 'func_name'):
                # function
                li.append(nodes.paragraph(text=el.func_name))
            else:
                # class             
                li.append(nodes.paragraph(text=el.__class__.__name__))
            ol.append(li)
        if exist:
            return ol
        return nodes.paragraph(text="-/-")
    
    def _doc_property(self, wpname):
        dl = nodes.definition_list_item()
        dl.append(nodes.term(text=wpname.split('.')[1]))
        propdoc = factory.doc['props'][wpname]
        dd = self._rest2node(propdoc, nodes.definition)
        dl.append(dd)
        return dl
    
    def _rest2node(self, rest, container=None):     
        vl = ViewList(prepare_docstring(rest))
        if container is None:
            node = nodes.container()
        else:
            node = container()
        nested_parse_with_titles(self.state, vl, node)        
        return node