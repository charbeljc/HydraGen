import logging
from typing import no_type_check_decorator

from clang.cindex import (
    Cursor,
    CursorKind,
    Index,
    TranslationUnit,
)
from logzero import logger

FLAGS = """-x c++ -c -fPIC -std=c++14 -fexceptions -DUSE_NAMESPACE=1
        -I/usr/include/c++/10/ -I/usr/include/x86_64-linux-gnu/c++/10/
        -I/usr/include/x86_64-linux-gnu/qt5/
        -I/usr/include/x86_64-linux-gnu/qt5/QtCore
        -I/usr/include/x86_64-linux-gnu/qt5/QtGui
        -I/usr/include/x86_64-linux-gnu/qt5/QtXml
        -I/home/rebelcat/Hack/hydrogen/src -I/home/rebelcat/Hack/hydrogen/build/src
        """.split()


def parse(path, flags=None):
    if flags is None:
        flags = FLAGS
    index = Index.create()
    tu = index.parse(
        path,
        flags,
        options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
    )
    for diag in tu.diagnostics:
        print(diag)
    return tu, index


def walk(root: Cursor, predicate):
    # print("node", root.kind)
    if predicate(root):
        yield root
    for node in root.get_children():
        yield from walk(node, predicate)


class NamedContainer:
    def __init__(self, name, node, parent=None):
        self.name = name
        self.parent = parent
        self.node = node
        self.content = {}
        self._fullname = None

    def get_root(self):
        if not self.parent:
            return self
        return self.parent.get_root()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.fullname!r}>"

    @property
    def fullname(self):
        if not self._fullname:
            self._fullname = (
                self.parent.fullname + "::" + self.name
                if self.parent and self.parent.name
                else self.name
            )
        return self._fullname

    def __getitem__(self, name_or_path):
        if isinstance(name_or_path, str):
            name_or_path = name_or_path.split("::")
        head, tail = name_or_path[0], name_or_path[1:]
        ns = self
        if not head:
            ns = self.get_root()
            head, tail = tail[0], tail[1:]
        sub = ns.content[head]
        if not tail:
            return sub
        return sub[tail]

    def __iter__(self):
        return self.content.__iter__()


class Namespace(NamedContainer):
    pass


class Function(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.inline = False
        self.arguments = []
        self.return_type = None
        self.overloads = []


class FunctionTemplate(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.inline = False
        self.type_parameters = []
        self.arguments = []
        self.return_type = None
        self.overloads = []


class Method(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.inline = False
        self.arguments = []
        self.return_type = None
        self.overloads = []


class Param(NamedContainer):
    pass


class Field(NamedContainer):
    pass


class Class(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.bases = []
        self.methods = []
        self.constructors = []
        self.destructors = []
        self.fields = []
        self.static_fields = []


class Struct(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.bases = []
        self.methods = []
        self.constructors = []
        self.destructors = []
        self.fields = []
        self.static_fields = []


class ClassTemplate(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.bases = []
        self.constructors = []
        self.destructors = []
        self.methods = []
        self.fields = []
        self.static_fields = []
        self.type_parameters = []
        self.instantiations = []


class ClassTemplatePartialSpecialization(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.bases = []
        self.constructors = []
        self.destructors = []
        self.methods = []
        self.fields = []
        self.static_fields = []
        self.type_parameters = []
        self.instantiations = []


class TypeDef(NamedContainer):
    pass


class TATD(NamedContainer):
    pass


class Enum(NamedContainer):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.__members__ = []

    pass


class Variable(NamedContainer):
    pass


class TypeRef(NamedContainer):
    pass


class TemplateTypeParam(NamedContainer):
    pass


class TxUnit(NamedContainer):
    def __init__(self, node, parent=None):
        super().__init__("", node, parent)


class Walker:
    deep: int = 0
    ns: Namespace = None
    current = None
    ctx = {}

    def __init__(self):
        self.ns = self.current = Namespace("", None)

    def say(self, *args):
        msg = " " * self.deep + " ".join(map(str, args))
        logger.info(msg)

    def huh(self, *args):
        msg = " " * self.deep + " ".join(map(str, args))
        logger.warning(msg)

    def walk_tu(self, node: Cursor):
        self.say("tu", node.spelling, node.location)
        assert CursorKind.is_translation_unit(node.kind)
        self.current = TxUnit(node, self.ns)
        for child in node.get_children():
            if child.kind == CursorKind.NAMESPACE:
                self.walk_namespace(child, Namespace)
            elif child.kind == CursorKind.FUNCTION_DECL:
                self.walk_function(child)
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_record(child, Class)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_record(child, Struct)
            elif child.kind == CursorKind.CLASS_TEMPLATE:
                self.walk_record(child, ClassTemplate)
            elif child.kind == CursorKind.ENUM_DECL:
                self.walk_enum(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.walk_class_template_partial_specialization(child)
            elif child.kind == CursorKind.VAR_DECL:
                self.walk_variable(child)
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            elif child.kind == CursorKind.CXX_METHOD:
                parent_node = child.semantic_parent
                self.say("method sem parent:", parent_node.kind, parent_node.spelling)
                parent = self.current.content.get(parent_node.spelling)
                self.say("method parent", parent)
            else:
                self.huh("tu: unhandled:", child.kind, child.displayname)

    def walk_typedef(self, node: Cursor):
        self.current.content[node.spelling] = TypeDef(node.spelling, node, self.current)

    def walk_variable(self, node: Cursor):
        self.current.content[node.spelling] = Variable(
            node.spelling, node, self.current
        )

    def walk_namespace(self, node: Cursor, Factory):
        self.say("namespace", node.spelling)
        ns = self.current.content.get(node.spelling)
        if not ns:
            ns = Factory(node.spelling, node, self.ns)
            self.current.content[node.spelling] = ns
        previous = self.current
        self.current = ns
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.NAMESPACE:
                self.walk_namespace(child, Namespace)
            elif child.kind == CursorKind.FUNCTION_DECL:
                self.walk_function(child)
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_record(child, Class)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_record(child, Struct)
            elif child.kind == CursorKind.CLASS_TEMPLATE:
                self.walk_record(child, ClassTemplate)
            elif child.kind == CursorKind.ENUM_DECL:
                self.walk_enum(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.walk_class_template_partial_specialization(child)
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            elif child.kind == CursorKind.VAR_DECL:
                self.walk_variable(child)
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            elif child.kind == CursorKind.CXX_METHOD:  # inline method def, for sure
                parent_node = child.semantic_parent
                self.say("method sem parent:", parent_node.kind, parent_node.spelling)
                parent = self.current.content.get(parent_node.spelling)
                if parent is None:
                    self.huh("could not find method parent in context", self.current)
                else:
                    self.say("method parent", parent)
            else:
                self.huh("ns: unhandled:", child.kind, child.displayname)
        self.deep -= 1
        # self.ns = self.current = self.ns.parent
        self.current = previous

    def walk_record(self, node: Cursor, Factory):
        self.say("class", node.spelling)
        cl = self.current.content.get(node.spelling)
        if not cl:
            cl = Factory(node.spelling, node, self.current)
            self.current.content[node.spelling] = cl
        self.current = cl
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.CXX_BASE_SPECIFIER:
                self.current.bases.append(child)
            elif child.kind == CursorKind.CXX_METHOD:
                m = Method(child.spelling, child, cl)
                self.current.methods.append(m)
                self.current.content[child.spelling] = m
            elif child.kind == CursorKind.FIELD_DECL:
                fld = Field(child.spelling, child, cl)
                self.current.fields.append(fld)
                self.current.content[child.spelling] = fld
            elif child.kind == CursorKind.VAR_DECL:
                fld = Field(child.spelling, child, cl)
                self.current.fields.append(fld)
                self.current.content[child.spelling] = fld
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                pass
            elif child.kind == CursorKind.ENUM_DECL:
                self.walk_enum(child)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_record(child, Struct)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_record(child, Class)
            elif child.kind == CursorKind.CLASS_TEMPLATE:
                self.walk_record(child, ClassTemplate)
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            elif child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                assert Factory is ClassTemplate
                self.current.type_parameters.append(
                    TemplateTypeParam(child.spelling, child, cl)
                )
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            else:
                self.huh("cl unhandled:", child.kind, child.spelling)
        self.current = self.current.parent
        self.deep -= 1

    def walk_function(self, node: Cursor):
        self.say("function", node.spelling)
        self.deep += 1
        f: Function = self.current.content.get(node.spelling)
        if f:
            self.say("overload")
            overload = Function(node.spelling, node, self.current)
            f.overloads.append(overload)
            f = overload
        else:
            f = Function(node.spelling, node, self.current)
            self.current.content[node.spelling] = f

        for child in node.get_children():
            if child.kind == CursorKind.PARM_DECL:
                f.arguments.append(Param(child.spelling, child, f))
            elif child.kind == CursorKind.TYPE_REF:
                f.return_type = TypeRef(child.spelling, child, f)
            elif child.kind == CursorKind.COMPOUND_STMT:
                f.inline = True
            else:
                self.say("fn unhandled:", child.kind, child.spelling, child.displayname)
        self.deep -= 1

    def show(self, caller: str, node: Cursor):
        self.say(caller, node.spelling)
        p = node.semantic_parent
        self.say("semantic parent", p.kind, p.spelling, p.displayname)
        p = node.lexical_parent
        self.say("lexical parent", p.kind, p.spelling, p.displayname)

    def walk_function_template(self, node: Cursor):
        self.show("function template", node)
        if node.spelling == "locale":
            breakpoint()
        self.deep += 1
        orphan = True
        ft = self.current.content.get(node.spelling)
        if ft:
            if isinstance(ft, FunctionTemplate):
                self.say("ft overload(1)", ft)
                overload = FunctionTemplate(node.spelling, node, self.current)
                ft.overloads.append(overload)
                ft = overload
                orphan = False
            elif isinstance(ft, Class):
                self.say("ft overload(2)", ft)
            else:
                self.say("ft overload(3)", ft)
        else:
            self.huh("no ft")

        ft = FunctionTemplate(node.spelling, node, self.current)
        self.current = ft
        for child in node.get_children():
            if child.kind == CursorKind.PARM_DECL:
                ft.arguments.append(Param(child.spelling, child, ft))
            elif child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                ttp = TemplateTypeParam(child.spelling, child, ft)
                ft.type_parameters.append(ttp)
                ft.content[child.spelling] = ttp
            elif child.kind == CursorKind.TYPE_REF:
                # ft.return_type = TypeRef(child.spelling, child, ft)
                self.say("TypeRef:", child.spelling)
                # cl = self.current[child.spelling]
                # self.say("found type ref", cl)
                # breakpoint()
                # bft = cl[ft.name]
                # self.say("found ft in type ref:", bft)
                # if bft:
                #     bft.overloads.append(ft)

            elif child.kind == CursorKind.COMPOUND_STMT:
                ft.inline = True
            else:
                self.huh("ft unhandled:", child.kind, child.spelling, child.displayname)
        self.current = self.current.parent
        if orphan:
            self.huh("orphan:", ft)
            if not self.current.content.get(ft.name):
                self.current.content[ft.name] = ft
        self.deep -= 1

    def walk_class_template_partial_specialization(self, node: Cursor):
        self.say("XXX class template partial specialization", node.spelling)
        # breakpoint()
        ct = self.current.content.get(node.spelling)
        if not ct:
            #
            # raise ValueError("class template not found")
            print(
                f"warning: template not found {node.spelling} in ns {self.current.fullname}"
            )
            return

        ctps = ClassTemplatePartialSpecialization(node.spelling, node, self.current)
        ct.instantiations.append(ctps)
        # self.current.content[node.spelling] = cl
        self.current = ctps
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.CXX_BASE_SPECIFIER:
                self.current.bases.append(child)
            elif child.kind == CursorKind.CXX_METHOD:
                self.current.methods.append(Method(child.spelling, child, ctps))
            elif child.kind == CursorKind.FIELD_DECL:
                self.current.fields.append(child)
            elif child.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                pass
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            elif child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                self.current.type_parameters.append(
                    TemplateTypeParam(child.spelling, child, ctps)
                )
            else:
                self.say("ctps unhandled:", child.kind, child.spelling)
        self.current = self.current.parent
        self.deep -= 1

    def walk_enum(self, node: Cursor):
        self.say("enum", node.spelling)
        self.current.content[node.spelling] = enum = Enum(node.spelling, node, self.ns)
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                enum.__members__.append(child)
            else:
                self.say("enum unhandled:", child.kind, child.spelling)
        self.deep -= 1
