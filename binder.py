from typing import no_type_check_decorator

from clang.cindex import Cursor, CursorKind, Index

FLAGS = """-x c++ -c -fPIC -std=c++14 -fexceptions -DUSE_NAMESPACE=1
        -I/usr/include/c++/10/ -I/usr/include/x86_64-linux-gnu/c++/10/
        -I/usr/include/x86_64-linux-gnu/qt5/
        -I/usr/include/x86_64-linux-gnu/qt5/QtCore
        -I/usr/include/x86_64-linux-gnu/qt5/QtGui
        -I/usr/include/x86_64-linux-gnu/qt5/QtXml
        -I/home/rebelcat/Hack/hydrogen/src -I/home/rebelcat/Hack/hydrogen/build/src
        """.split()


def parse(path, flags=None):
    if flags is None: flags = FLAGS
    index = Index.create()
    tu = index.parse('/home/rebelcat/Hack/hydrogen/src/pybind11_bindings/core_bindings.h', flags)
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
        return f'<{self.__class__.__name__} {self.fullname!r}>'

    @property
    def fullname(self):
        if not self._fullname:
            self._fullname = self.parent.fullname + "::" + self.name if self.parent and self.parent.name else self.name
        return self._fullname

    def __getitem__(self, name_or_path):
        if isinstance(name_or_path, str):
            name_or_path = name_or_path.split('::')
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
        super(Class, self).__init__(name, node, parent)
        self.bases = []
        self.methods = []
        self.constructors = []
        self.destructors = []
        self.fields = []
        self.static_fields = []

class Struct(NamedContainer):
    def __init__(self, name, node, parent=None):
        super(Struct, self).__init__(name, node, parent)
        self.bases = []
        self.methods = []
        self.constructors = []
        self.destructors = []
        self.fields = []
        self.static_fields = []

class ClassTemplate(NamedContainer):
    def __init__(self, name, node, parent=None):
        super(ClassTemplate, self).__init__(name, node, parent)
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
        super(ClassTemplatePartialSpecialization, self).__init__(name, node, parent)
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
        super(Enum, self).__init__(name, node, parent)
        self.__members__ = []
    pass

class Variable(NamedContainer):
    pass
class TypeRef(NamedContainer):
    pass

class TemplateTypeParam(NamedContainer):
    pass

class Walker:
    deep: int = 0
    ns: Namespace = None
    current = None

    def __init__(self):
        self.ns = self.current = Namespace("", None)

    def say(self, *args):
        print(" " * self.deep, *args)

    def walk_tu(self, node: Cursor):
        assert CursorKind.is_translation_unit(node.kind)
        for child in node.get_children():
            if child.kind == CursorKind.NAMESPACE:
                self.walk_namespace(child)
            elif child.kind == CursorKind.FUNCTION_DECL:
                self.walk_function(child)
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_class(child)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_struct(child)
            elif child.kind == CursorKind.ENUM_DECL:
                self.walk_enum(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE:
                self.walk_class_template(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.walk_class_template_partial_specialization(child)
            elif child.kind == CursorKind.VAR_DECL:
                self.walk_variable(child) 
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            else:
                self.say("tu: unhandled:", child.kind, child.displayname)

    def walk_typedef(self, node: Cursor):
        self.current.content[node.spelling] = TypeDef(node.spelling, node, self.current)


    def walk_variable(self, node: Cursor):
        self.current.content[node.spelling] = Variable(node.spelling, node, self.current)

    def walk_namespace(self, node: Cursor):
        self.say("namespace", node.spelling)
        ns = self.ns.content.get(node.spelling)
        if not ns:
            ns = Namespace(node.spelling, node, self.ns)
            self.ns.content[node.spelling] = ns
        self.ns = self.current = ns
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.NAMESPACE:
                self.walk_namespace(child)
            elif child.kind == CursorKind.FUNCTION_DECL:
                self.walk_function(child)
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_class(child)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_struct(child)
            elif child.kind == CursorKind.ENUM_DECL:
                self.walk_enum(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE:
                self.walk_class_template(child)
            elif child.kind == CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
                self.walk_class_template_partial_specialization(child)
            elif child.kind == CursorKind.VAR_DECL:
                self.walk_variable(child) 
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            elif child.kind == CursorKind.CXX_METHOD:  # inline method def, for sure
                pass
            else:
                self.say("ns: unhandled:", child.kind, child.displayname)
        self.deep -= 1
        self.ns = self.current = self.ns.parent

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
                f.arguments.append( Param(child.spelling, child, f) )
            elif child.kind == CursorKind.TYPE_REF:
                f.return_type = TypeRef(child.spelling, child, f)
            elif child.kind == CursorKind.COMPOUND_STMT:
                f.inline = True
            else:
                self.say("fn unhandled:", child.kind, child.spelling, child.displayname)
        self.deep -= 1

    def walk_function_template(self, node: Cursor):
        self.say("function template", node.spelling)
        self.deep += 1
        ft = self.current.content.get(node.spelling)
        if ft:
            if isinstance(ft, FunctionTemplate):
                self.say("ft overload")
                overload = FunctionTemplate(node.spelling, node, self.current)
                ft.overloads.append(overload)
                ft = overload
        else:
            ft = FunctionTemplate(node.spelling, node, self.current)
            self.current.content[node.spelling] = ft

        for child in node.get_children():
            if child.kind == CursorKind.PARM_DECL:
                ft.arguments.append( Param(child.spelling, child, ft) )
            elif child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                ft.type_parameters.append (TemplateTypeParam(child.spelling, child, ft))
            elif child.kind == CursorKind.TYPE_REF:
                ft.return_type = TypeRef(child.spelling, child, ft)
            elif child.kind == CursorKind.COMPOUND_STMT:
                ft.inline = True
            else:
                self.say("ft unhandled:", child.kind, child.spelling, child.displayname)
        self.deep -= 1

    def walk_class(self, node: Cursor):
        self.say("class", node.spelling)
        cl = self.current.content.get(node.spelling)
        if not cl:
            cl = Class(node.spelling, node, self.current)
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
                self.walk_struct(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_class(child)
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            else:
                self.say("cl unhandled:", child.kind, child.spelling)
        self.current = self.current.parent
        self.deep -= 1

    def walk_struct(self, node: Cursor):
        self.say("class", node.spelling)
        cl = self.current.content.get(node.spelling)
        if not cl:
            cl = Struct(node.spelling, node, self.current)
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
                self.walk_struct(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_class(child)
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            else:
                self.say("struct unhandled:", child.kind, child.spelling)
        self.current = self.current.parent
        self.deep -= 1

    def walk_class_template(self, node: Cursor):
        self.say("class template", node.spelling)
        cl = self.current.content.get(node.spelling)
        if not cl:
            cl = ClassTemplate(node.spelling, node, self.current)
            self.current.content[node.spelling] = cl
        self.current = cl
        self.deep += 1
        for child in node.get_children():
            if child.kind == CursorKind.CXX_BASE_SPECIFIER:
                self.current.bases.append(child)
            elif child.kind == CursorKind.CXX_METHOD:
                self.current.methods.append(Method(child.spelling, child, cl))
            elif child.kind == CursorKind.FIELD_DECL:
                self.current.fields.append(child)
            elif child.kind == CursorKind.CLASS_DECL:
                self.walk_class(child)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.walk_struct(child)
            elif child.kind == CursorKind.FUNCTION_TEMPLATE:
                self.walk_function_template(child)
            elif child.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                pass
            elif child.kind == CursorKind.CONSTRUCTOR:
                self.current.constructors.append(child)
            elif child.kind == CursorKind.DESTRUCTOR:
                self.current.destructors.append(child)
            elif child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                self.current.type_parameters.append(TemplateTypeParam(child.spelling, child, cl))
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.walk_typedef(child)
            else:
                self.say("tc unhandled:", child.kind, child.spelling)
        self.current = self.current.parent
        self.deep -= 1

    def walk_class_template_partial_specialization(self, node: Cursor):
        self.say("XXX class template partial specialization", node.spelling)
        # breakpoint()
        ct = self.current.content.get(node.spelling)
        if not ct:
            #
            # raise ValueError("class template not found")
            print(f"warning: template not found {node.spelling} in ns {self.current.fullname}")
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
                self.current.type_parameters.append(TemplateTypeParam(child.spelling, child, ctps))
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
