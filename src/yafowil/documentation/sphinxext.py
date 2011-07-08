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
from yafowil.utils import UNSET

_marker = list()

class WidgetDoc(Directive):
    
    def run(self):
        result = []
        for key in sorted(factory._factories.keys()):
            if factory.doc['widget'].get(key, None) is UNSET:
                continue
            result.append(self._doc_widget(key))
        return result        
    
    def _managed_props_of(self, widgetname):
        props = set([_ for _ in factory.doc['props'] 
                     if _.startswith('%s.' % widgetname)])
        for chainidx in range(0,4):
            chain = factory._factories[widgetname][chainidx]
            for func in chain:
                mprops = getattr(func, '__yafowil_managed_props__', [])
                props.update(['%s.%s' % (widgetname, _) for _ in mprops])
        return sorted(props)
    
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
        +------------+----------------+---------------+----------+-------------------+
        | extractors | edit_renderers | preprocessors | builders | display_renderers |
        +============+================+===============+==========+===================+
        | replace    | replace        | replace       | replace  | replace           |
        +------------+----------------+---------------+----------+-------------------+
        """
        table = self._rest2node(table)        
        rub.append(table)
        row = table.children[0].children[0].children[5].children[0]
        for idx in range(0,5):
            row[idx].children = []
            row[idx].append(self._doc_chain(widgetname, idx))      

        # document properties
        rub = nodes.rubric(text='Properties')
        sec.append(rub)
        table= """
        +----------+---------+-------------+
        | property | default | description |
        +==========+=========+=============+
        | replace  | replace | replace     |
        +----------+---------+-------------+
        """   
        table = self._rest2node(table)              
        table.children[0].children[0].children[4].children = []
        rub.append(table)
        for prop in self._managed_props_of(widgetname):
            table.children[0].children[0].children[4].append(
                                                       self._doc_property(prop))
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
        widget, prop =  wpname.split('.')
        table= """
        +----------+---------+-------------+
        | property | default | description |
        +==========+=========+=============+
        | replace  | replace | replace     |
        +----------+---------+-------------+
        """   
        table = self._rest2node(table)      
        row = table.children[0].children[0].children[4].children[0]
        row[0].children = []
        row[1].children = []
        row[2].children = []
        row[0].append(nodes.paragraph(text=prop))      
        
        default = factory.defaults.get(wpname, _marker)        
        if default is not _marker:
            row[1].append(nodes.literal(text=repr(default)))
        else:
            default = factory.defaults.get(prop, _marker)
            if default is not _marker:
                row[1].append(nodes.literal(text=repr(default)))
                row[1].append(nodes.emphasis(text=' global'))
            else:
                row[1].append(nodes.emphasis(text='required/ not set'))                
        
        doc = factory.doc['props'].get(wpname, 
                                       factory.doc['props'].get(prop, _marker))
        if doc is not _marker:
            row[2].append(self._rest2node(doc))
        else:
            row[2].append(nodes.paragraph('(not documented)'))
            # this does not log. bullshit. no idea how to make sphinx log.         
            self.warning("YAFOWIL property '%s' is not documented!" % wpname)
        return row
    
    def _rest2node(self, rest, container=None):     
        vl = ViewList(prepare_docstring(rest))
        if container is None:
            node = nodes.container()
        else:
            node = container()
        nested_parse_with_titles(self.state, vl, node)        
        return node