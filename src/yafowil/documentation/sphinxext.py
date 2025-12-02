import yafowil.loader
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.nodes import nested_parse_with_titles
from yafowil.base import factory
from yafowil.utils import UNSET
import inspect

try:
    from sphinx.util.compat import Directive
except ImportError:
    from docutils.parsers.rst import Directive


_marker = list()


class YDirective(Directive):
    def _rest2node(self, rest, container=None):
        vl = ViewList(prepare_docstring(rest))
        if container is None:
            node = nodes.container()
        else:
            node = container()
        nested_parse_with_titles(self.state, vl, node)
        return node


class WidgetDoc(YDirective):
    def run(self):
        result = []
        for key in sorted(factory._blueprints.keys()):
            if factory.doc["blueprint"].get(key, None) is UNSET:
                continue
            result.append(self._doc_widget(key))
        return result

    def _managed_props_of(self, widgetname):
        props = set(
            [_ for _ in factory.doc["props"] if _.startswith("%s." % widgetname)]
        )
        for chainidx in range(0, 5):
            chain = factory._blueprints[widgetname][chainidx]
            for func in chain:
                mprops = getattr(func, "__yafowil_managed_props__", [])
                props.update(["%s.%s" % (widgetname, _) for _ in mprops])
        return sorted(props)

    def _doc_widget(self, widgetname):
        sec = nodes.section()
        sec["ids"].append(widgetname)
        # set a title:
        sec.append(nodes.title(text=widgetname))
        # fetch main documentation
        maindoc = factory.doc["blueprint"].get(widgetname, None)
        if maindoc is not None:
            sec.append(self._rest2node(maindoc))
        else:
            sec.append(nodes.paragraph(text="This widget is currently undocumented."))

        # document properties
        rub = nodes.subtitle(text="Properties")
        sec.append(rub)
        table = """
        +----------+---------+-------------+
        | name     | default | description |
        +==========+=========+=============+
        | replace  | replace | replace     |
        +----------+---------+-------------+
        """
        table = self._rest2node(table)
        table.children[0].children[0].children[4].children = []
        rub.append(table)
        for prop in self._managed_props_of(widgetname):
            table.children[0].children[0].children[4].append(self._doc_property(prop))

        # build table of callables used
        rub = nodes.subtitle(text="Chains")
        sec.append(rub)
        table = """\
        +------------+----------------+-------------------+---------------+----------+
        | extractors | edit renderers | display renderers | preprocessors | builders |
        +============+================+===================+===============+==========+
        | replace    | replace        | replace           | replace       | replace  |
        +------------+----------------+-------------------+---------------+----------+
        """
        table = self._rest2node(table)
        rub.append(table)
        row = table.children[0].children[0].children[6].children[0]
        for col, idx in [(0, 0), (1, 1), (2, 4), (3, 2), (4, 3)]:
            row[col].children = []
            row[col].append(self._doc_chain(widgetname, idx))
        return sec

    def _doc_chain(self, widgetname, chainidx):
        ol = nodes.enumerated_list()
        chain = factory._blueprints[widgetname][chainidx]
        exist = False
        for el in chain:
            exist = True
            li = nodes.list_item()
            if inspect.isfunction(el):
                li.append(nodes.paragraph(text=el.__name__))
            else:
                li.append(nodes.paragraph(text=el.__class__.__name__))
            ol.append(li)
        if exist:
            return ol
        return nodes.paragraph(text="-/-")

    def _doc_property(self, wpname):
        blueprint_name, prop = wpname.split(".")
        table = """
        +----------+---------+-------------+
        | name     | default | description |
        +==========+=========+=============+
        | replace  | replace | replace     |
        +----------+---------+-------------+
        """
        table = self._rest2node(table)
        row = table.children[0].children[0].children[4].children[0]
        row[0].children = []
        row[1].children = []
        row[2].children = []

        row[0].append(nodes.strong(text=prop))

        default = factory.defaults.get(wpname, _marker)
        if default is not _marker:
            row[1].append(nodes.literal(text=repr(default)))
        else:
            default = factory.defaults.get(prop, _marker)
            if default is not _marker:
                row[1].append(nodes.literal(text=repr(default)))
                row[1].append(nodes.emphasis(text=" global"))
            else:
                row[1].append(nodes.emphasis(text="required/ not set"))

        doc = factory.doc["props"].get(wpname, factory.doc["props"].get(prop, _marker))
        if doc is not _marker:
            row[2].append(self._rest2node(doc))
        else:
            row[2].append(nodes.paragraph("(not documented)"))
            # this does not log. bullshit. no idea how to make sphinx log
            print("YAFOWIL property '%s' is not documented!" % wpname)

        ul = nodes.bullet_list()
        used = []

        def add_chain_for_property(chain):
            for el in chain:
                if prop not in getattr(el, "__yafowil_managed_props__", []):
                    # if getattr(el, '__yafowil_managed_props__', True):
                    # print ('YAFOWIL callable %s has no ' % el,
                    #       'managed props decorator!')
                    continue
                li = nodes.list_item()
                if inspect.isfunction(el):
                    name = el.__name__
                else:
                    name = el.__class__.__name__
                if name in used:
                    continue
                used.append(name)
                li.append(nodes.emphasis(text=name))
                ul.append(li)

        add_chain_for_property(factory.extractors(blueprint_name))
        add_chain_for_property(factory.edit_renderers(blueprint_name))
        add_chain_for_property(factory.display_renderers(blueprint_name))
        add_chain_for_property(factory.builders(blueprint_name))
        add_chain_for_property(factory.preprocessors(blueprint_name))
        if not used:
            print("YAFOWIL property '%s' is not handled by managed props!" % wpname)

        if len(ul):
            row[2].append(nodes.field_name(text="Used by:"))
            row[2].append(ul)

        return row


class PlanDoc(YDirective):
    def run(self):
        result = []
        result.append(self._doc_plans())
        return result

    def _doc_plans(self):
        table = """
        +------+------------+
        | plan | blueprints |
        +======+============+
        | repl | replace    |
        +------+------------+
        """
        table = self._rest2node(table)
        rows = table.children[0].children[0].children[3].children[0]
        rows[0].children = []
        rows[1].children = []

        for macro, blueprints in sorted(factory._macros.items()):
            rows[0].append(nodes.paragraph(text=macro))
            rows[1].append(nodes.paragraph(text=":".join(blueprints)))
        return table
