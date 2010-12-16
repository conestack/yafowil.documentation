# -*- coding: utf-8 -*-
from docutils import nodes
from docutils.utils import new_document
from sphinx.ext.autodoc import AutoDirective
from sphinx.ext.autodoc import FunctionDocumenter

import yafowil.loader

class WidgetDoc(AutoDirective):

    has_content = True
    required_arguments = 0

    def run(self):
        print "I'am running away!"
        return []
        
    def notrun(self):
        self.load_agx_config()
        agx_defs = self.read_agx()
        ret = list()
        old_name = self.name
        self.name = 'autofunction'
        for transform in agx_defs:
            for generator in transform['generators']:
                sec = nodes.section()
                sec['ids'].append(generator['name'])
                text = "%s" % generator['name'].replace('.', ' - ')
                gen = nodes.subtitle(text=text)
                sec.append(gen)
                ret.append(sec)
                
                description = generator['description']
                if description:
                    desc = nodes.paragraph(text=description)
                    sec.append(desc)
                
                for handler in generator['handler']:
                    name = handler['name']
                    self.arguments = [handler['package_path']]
                    doc = AutoDirective.run(self)
                    sec += doc
                    body = doc[1].children[-1]
                    position = len(doc[1].children[-1]) - 2
                    
                    dl = nodes.definition_list()
                    body.insert(position, dl)
                    
                    iname = name[:name.find('.')]
                    dl.append(self._definition_item('Transform', iname))
                    
                    iname = name[name.find('.') + 1:name.rfind('.')]
                    dl.append(self._definition_item('Generator', iname))
                    
                    scope = handler['scope']
                    if scope is not None:
                        modulename = scope['class'].__module__
                        classname = scope['class'].__name__
                        iname = "%s.%s" % (modulename, classname)
                        dl.append(self._definition_item('Scope', iname))
                    
                    iname = handler['order']
                    dl.append(self._definition_item('Order', iname))
        self.name = old_name
        return ret

    def _definition_item(self, term, classifier):
        item = nodes.definition_list_item()
        term = nodes.term(text=term)
        item.append(term)
        classifier = nodes.classifier(text=classifier)
        item.append(classifier)
        return item