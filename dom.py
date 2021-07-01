from __future__ import annotations

import sys
from collections import abc
import typing
from typing_extensions import TypeAlias

from clang.cindex import (
    AccessSpecifier,
    Cursor,
    CursorKind,
    FileInclusion,
    Index,
    TranslationUnit,
    Type,
    TypeKind,
)
from logzero import logger
from orderedset import OrderedSet


def kind(node):
    return (
        ("%s:%r" % (node.kind, node.spelling))[len("CursorKind.") :] if node else None
    )


class Config:
    pass


class Context:

    factory: dict[CursorKind, abc.Callable[[Context, Cursor], NodeProxy | None]]
    config: Config
    elements: dict[str, NodeProxy]  # key is clang node's usr
    builtins: dict[str, NodeProxy]
    flags: list[str]
    plugins: list[str]
    _casters: dict[NodeProxy, NodeProxy] | None
    _tx : TxUnit | None

    def __init__(self, factory: dict[CursorKind, type], config: Config):
        self.factory = factory
        self.config = config
        self.elements = {}
        self.builtins = {}
        self.stack = []
        self.flags = []
        self.plugins = []
        self.index = Index.create()
        self._casters = None

    def set_flags(self, flags: str | list[str]):
        if isinstance(flags, str):
            self.flags = flags.strip().split()
        else:
            self.flags = flags[:]
        return self

    def add_flag(self, flag: str):
        flag = flag.strip()
        self.flags.append(flag)
        return self

    def add_pybind11_plugin(self, plugin):
        """TODO: doc"""
        self.plugins.append(plugin)
        return self

    def parse(self, path) -> tuple[TxUnit, list[Include]]:
        tu = self.index.parse(
            path,
            self.flags,
            options=TranslationUnit.PARSE_INCOMPLETE
            | TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
        )
        for diag in tu.diagnostics:
            print(diag, file=sys.stderr)
        includes = [Include(inc) for inc in tu.get_includes()]
        self._tx = typing.cast(TxUnit, self.make(tu.cursor))
        return self._tx, includes

    def parse_plugins(self):
        from gen import generate_includes

        code = []
        generate_includes(["pybind11/pybind11.h"] + self.plugins, code)
        with open("_plugins.hpp", "w") as src:
            src.write("".join(code))
        tx, incl = self.parse("_plugins.hpp")
        return tx, incl

    def casters(self):
        _casters = {}
        if not self._tx:
            return {}
        for casting in self._tx['pybind11::detail::type_caster']:
            tref = list(casting._filter(TypeRef))
            if tref:
                _casters[tref[0].type] = casting
        return _casters

    def push(self, node: NodeProxy):
        self.stack.append(node)
        return self

    def pop(self, node: NodeProxy):
        check = self.stack.pop()
        assert node is check
        return self

    def indent(self) -> str:
        return " " * len(self.stack)

    @property
    def top(self) -> NodeProxy | None:
        if self.stack:
            return self.stack[-1]
        else:
            return None

    def make(self, node: Cursor) -> NodeProxy | None:
        usr = node.get_usr()
        obj = None
        if self.factory.get(node.kind):
            # logger.debug("FACT %s %r, parent: %s", kind(node), usr, kind(node.semantic_parent))
            if usr:
                obj = self.elements.get(usr)
                if not obj:
                    self.elements[usr] = obj = self.factory[node.kind](self, node)
                else:
                    obj.accept_occurence(node)
            else:
                obj = self.factory[node.kind](self, node)
        return obj

    def make_builtin(self, type_: Type) -> NodeProxy:
        node = self.builtins.get(type_.spelling)
        if not node:
            node = Builtin(self, type_)
            self.builtins[type_.spelling] = node
        return node


class Include:
    _clang: FileInclusion

    def __init__(self, fi: FileInclusion):
        self._clang = fi

    def __repr__(self):
        return f"<include {self.depth} {self.path!r}>"

    @property
    def depth(self):
        return self._clang.depth

    @property
    def path(self):
        return self._clang.include.name


class Binder:
    def bind(self, node):
        logger.info("TODO: binding: %s", node)


class Bindable:
    def bind(self, binder: Binder):
        binder.bind(self)

    def is_bindable(self):
        return True


class NodeProxy:
    name: str
    node: Cursor
    context: Context
    parent: NodeProxy | None
    content: dict

    def __init__(self, context: Context, node: Cursor, parent: NodeProxy | None = None):
        self.context = context
        self.name = node.spelling or node.get_usr()
        self.parent = parent
        self.node = node
        self.content = {}
        self._fullname = None
        self._usr = None

    def get_root(self):
        if not self.parent:
            return self
        return self.parent.get_root()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.displayname!r}>"  # {self.usr!r}>"

    def accept(self, item):
        if not self.allowed(item):
            logger.debug("reject %s item %s", self, item)
            return False
        if item == self:
            logger.debug("ACCEPT SELF: %s", item)
            return True
        ### FIXME: move to allowed
        if (
            item.node.semantic_parent
            and item.kind
            not in (
                CursorKind.TEMPLATE_TYPE_PARAMETER,
                CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
            )
            # and item.node.semantic_parent.kind != CursorKind.TRANSLATION_UNIT
            and item.node.semantic_parent.get_usr() != self.node.get_usr()
        ):
            logger.debug(
                "reject (not parent) %s, item: %s, parent: %s",
                self,
                item,
                kind(item.node.semantic_parent),
            )
            return False
        logger.debug("ACCEPT: %s, item %s, loc: %s", self, item, item.location)
        if self.name == "is_array" and item.name == "__not_":
            breakpoint()
        if not isinstance(item, Pop):
            self.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(self, TxUnit):
                item.parent = self
        return True

    def accept_occurence(self, node: Cursor):
        if isinstance(self, Callable):
            logger.warning("new occurence of %s: %s", self, node)
        if not self.content:
            self.node = node

    def is_bindable(self):
        return False

    def allowed(self, item):
        return False

    def check_parent(self, item: NodeProxy):
        item_parent = item.node.semantic_parent
        if (
            item_parent
            and item_parent.get_usr()
            and item_parent.get_usr() != self.node.get_usr()
        ):
            if item.kind in (
                CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
                CursorKind.TEMPLATE_TYPE_PARAMETER,
            ):
                return True
            logger.warn("%s not parent of %s (%s)", self, item, item_parent.kind)
            return False
        return True

    def walk(self, node=None):
        if node is None:
            node = self.node
        else:
            if self.node.kind != node.kind:
                logger.debug(
                    "walk on different child type: self :%s, node:%s\n"
                    "self: %s: %s\nother: %s: %s",
                    self.node.kind,
                    node.kind,
                    self.node.spelling,
                    self.node.location,
                    node.spelling,
                    node.location,
                )
        self.context.push(self)
        for child in node.get_children():
            obj = self.context.make(child)
            if obj:
                ok = self.accept(obj)
                if not ok and (isinstance(obj, Enum) or isinstance(self, Enum)):
                    logger.warning("Enum! %s, self: %s", obj, self)
                obj.walk(child)
            else:
                if isinstance(self, Enum):
                    logger.warning("Enum!! %s %r", child.kind, child.spelling)
        self.context.pop(self)
        return self

    def is_builtin(self):
        return False

    @property
    def namespaces(self):
        return list(self._filter(Namespace))

    @property
    def displayname(self):
        return self.node.displayname

    def is_public(self):
        return self.node.access_specifier == AccessSpecifier.PUBLIC

    def is_protected(self):
        return self.node.access_specifier == AccessSpecifier.PROTECTED

    def is_private(self):
        return self.node.access_specifier == AccessSpecifier.PRIVATE

    @property
    def kind(self):
        return self.node.kind

    @property
    def location(self):
        return self.node.location

    @property
    def fullname(self):
        if self._fullname is None:
            self._fullname = (
                self.parent.fullname + "::" + self.name
                if self.parent and self.parent.name
                else self.name
            )
        return self._fullname

    @property
    def usr(self):
        if self._usr is None:
            self._usr = self.node.get_usr()
        return self._usr or None

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
            if len(sub) == 1:
                (sub,) = sub
            return sub
        elif len(sub) == 1:
            (sub,) = sub
        return sub[tail]

    def __iter__(self):
        return self.content.__iter__()

    def _filter(self, types, predicate=None):
        if not predicate:
            predicate = lambda _: True
        for objs in self.content.values():
            for obj in objs:
                if isinstance(obj, types) and predicate(obj):
                    yield obj

    @property
    def dependencies(self) -> set[NodeProxy]:
        return OrderedSet()


class Builtin(NodeProxy):
    def __init__(self, context: Context, type_: Type, parent: NodeProxy | None = None):
        super().__init__(context, type_.get_declaration(), parent)
        self.type_ = type_
        self.name = type_.spelling

    @property
    def displayname(self):
        return self.name

    def is_builtin(self):
        return True


class Namespace(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.FUNCTION_DECL,
            CursorKind.FUNCTION_TEMPLATE,
            CursorKind.STRUCT_DECL,
            CursorKind.ENUM_DECL,
            CursorKind.CLASS_DECL,
            CursorKind.CLASS_TEMPLATE,
            CursorKind.NAMESPACE,
            CursorKind.TYPEDEF_DECL,
            CursorKind.TYPE_ALIAS_TEMPLATE_DECL,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class TypeHolder(NodeProxy):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.type_ = None

    def _get_clang_type(self) -> Type:
        check = self.node.type
        if check.kind == TypeKind.INVALID:
            raise ValueError
        return check

    def _compute_type(self) -> NodeProxy | None:
        """ This sucks ... """
        node = None
        t = self._get_clang_type()
        assert t.kind != TypeKind.INVALID
        type_ref = list(self._filter(TypeRef))
        if type_ref:
            if len(type_ref) != 1:
                logger.warn(
                    "mutiple typerefs: %s: assuming last is return type: %s",
                    self,
                    type_ref,
                )
            type_ref = type_ref[-1]
            decl = type_ref.node.get_definition()
            if decl:
                node = self.context.elements[decl.get_usr()]
        else:
            pointee = t.get_pointee()
            if pointee.kind != TypeKind.INVALID:
                decl = pointee.get_declaration()
            else:
                decl = t.get_declaration()
            if decl.kind == CursorKind.NO_DECL_FOUND:
                return self.context.make_builtin(t)
            if decl:
                defi = decl.get_definition()
                if defi:
                    try:
                        node = self.context.elements[defi.get_usr()]
                    except KeyError:
                        logger.warning("lookup failed(def): %s %s %s", defi.kind, defi.spelling, defi.get_usr())
                else:
                    try:
                        node = self.context.elements[decl.get_usr()]
                    except KeyError:
                        logger.warning("lookup failed(decl): %s %s %s", decl.kind, decl.spelling, decl.get_usr())

        if not node:
            logger.warning("_compute_type() failed for %s", self)
        return node

    @property
    def type(self) -> NodeProxy:
        if self.type_ is None:
            self.type_ = self._compute_type()
        return self.type_

    @property
    def dependencies(self) -> set[NodeProxy]:
        deps = OrderedSet()
        type_ = self.type
        if not type_:
            logger.warning("no type for %s", self)
        if type_ and not type_.is_builtin():
            if isinstance(type_, (TemplateRef, TypeRef)):
                deps.add(type_.type)
            elif isinstance(type_, TypeAliasDecl):
                deps |= type_.dependencies
            else:
                deps.add(type_)
        return deps


class Callable(TypeHolder):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.inline = False
        self.overloads = []
        self._return_type = None
        self._cpp_signature = None
        self._parameters = None

    def _get_clang_type(self):
        return self.node.result_type

    def _get_clang_signature(self):
        return self.node.type

    def accept_occurence(self, node: Cursor):
        self.content = {}
        self.node = node
        self.inline = True
        self._return_type = None
        self._cpp_signature = None
        self._parameters = None

    def allowed(self, item) -> bool:
        if item.kind in (
            CursorKind.PARM_DECL,
            CursorKind.TYPE_REF,
        ):
            return True
        return super().allowed(item)

    @property
    def cpp_signature(self) -> str:
        if self._cpp_signature is None:
            self._cpp_signature = self.displayname.split("(")[1].split(")")[0]
        return self._cpp_signature

    @property
    def parameters(self) -> list[Param]:
        if self._parameters is None:
            self._parameters = list(self._filter(Param))
        return self._parameters

    @property
    def dependencies(self) -> set[NodeProxy]:
        deps = super().dependencies
        for param in self.parameters:
            deps |= param.dependencies
        return deps


class Function(Callable, Bindable):
    pass


class FunctionTemplate(Callable):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class Method(Callable):
    def is_static(self):
        return self.node.is_static_method()
    def is_virtual(self):
        return self.node.is_virtual_method()
    def is_pure_virtual(self):
        return self.node.is_pure_virtual_method()


class TypeRef(TypeHolder):
    pass


class TemplateRef(TypeHolder):
    def _compute_type(self) -> NodeProxy:
        type_ref = self.node.get_definition()
        return self.context.elements[type_ref.get_usr()]

    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            CursorKind.TYPE_ALIAS_DECL,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class TypeAliasDecl(TypeHolder):
    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            return self.check_parent(item)
        return super().allowed(item)

    @property
    def dependencies(self) -> set[NodeProxy]:
        deps = OrderedSet()
        for type_ in self._filter((TemplateRef, TypeRef)):
            deps.add(type_)
        return deps


class Param(TypeHolder):
    def _get_clang_type(self) -> Type:
        type_ = self.node.type
        while type_.kind == TypeKind.POINTER:
            type_ = type_.get_pointee()
        if type_.kind == TypeKind.INVALID:
            raise ValueError("could not get type for %s" % self)
        return type_

    def _compute_type(self) -> NodeProxy | None:
        st = super()._compute_type()
        if not st:
            logger.warning("hu... %s", self)
            type_ = self._get_clang_type()
            st = self.context.elements.get(type_.get_declaration().get_usr())
        return st

    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            return self.check_parent(item)
        return super().allowed(item)


class Field(TypeHolder):
    pass


class Pop(NodeProxy):
    pass


class TxUnit(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.FUNCTION_DECL,
            CursorKind.FUNCTION_TEMPLATE,
            CursorKind.STRUCT_DECL,
            CursorKind.CLASS_DECL,
            CursorKind.CLASS_TEMPLATE,
            CursorKind.NAMESPACE,
            CursorKind.UNEXPOSED_DECL,
            CursorKind.ENUM_DECL,
            CursorKind.TYPEDEF_DECL,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class BaseSpecifier(TypeHolder):
    def _get_clang_type(self):
        type_ref, *tail = self._filter(TypeRef)
        if tail:
            logger.debug("BaseSpecifier: template? %s %s", type_ref, tail)
        return type_ref.node.type

    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class Record(NodeProxy):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self._bases = None
        self._methods = None
        self._constructors = None
        self._destructors = None
        self._fields = None
        self.static_fields = None

    def allowed(self, item):
        if item.kind in (
            CursorKind.FIELD_DECL,
            CursorKind.CXX_METHOD,
            CursorKind.VAR_DECL,
            CursorKind.CONSTRUCTOR,
            CursorKind.DESTRUCTOR,
            CursorKind.TYPE_ALIAS_DECL,
            CursorKind.CXX_BASE_SPECIFIER,
            CursorKind.CLASS_TEMPLATE,
            CursorKind.CLASS_DECL,
            CursorKind.ENUM_DECL,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
            CursorKind.TYPE_REF,
            CursorKind.TYPEDEF_DECL,
            CursorKind.FUNCTION_TEMPLATE,
        ):
            return self.check_parent(item)
        return super().allowed(item)

    def is_abstract(self):
        return self.node.is_abstract_record()

    @property
    def bases(self) -> list[Record]:
        if self._bases is None:
            bases = []
            for spec in self._filter(BaseSpecifier):
                node = spec.type
                assert node
                bases.append(node)
            self._bases = bases
        return self._bases

    @property
    def constructors(self) -> list[Constructor]:
        if self._constructors is None:
            self._constructors = list(self._filter(Constructor))
        return self._constructors

    @property
    def destructors(self) -> list[Destructor]:
        if self._destructors is None:
            self._destructors = list(self._filter(Destructor))
        return self._destructors

    @property
    def methods(self) -> list[Method]:
        if self._methods is None:
            self._methods = list(self._filter(Method))
        return self._methods

    @property
    def fields(self) -> list[Field]:
        if self._fields is None:
            self._fields = list(self._filter(Field))
        return self._fields

    @property
    def dependencies(self) -> set[Record]:
        deps = OrderedSet()
        if self.parent and isinstance(self.parent, Record):
            deps.add(self.parent)
        for base in self.bases:
            deps.add(base)
        return deps


class Class(Bindable, Record):
    pass

class Struct(Bindable, Record):
    pass

class ClassTemplate(Record):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.type_parameters = []
        self.instantiations = []

    def allowed(self, item):
        if item.kind in (
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
            CursorKind.TYPEDEF_DECL,
            CursorKind.FUNCTION_TEMPLATE,
            CursorKind.TEMPLATE_REF,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class ClassTemplatePartialSpecialization(Record):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.type_parameters = []
        self.instantiations = []

    def allowed(self, item):
        if item.kind in (
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
            CursorKind.TYPEDEF_DECL,
            CursorKind.TYPE_REF,
            CursorKind.FUNCTION_TEMPLATE,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class TypeDef(NodeProxy):
    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF, CursorKind.ENUM_DECL):
            return self.check_parent(item)
        return super().allowed(item)


class Enum(Bindable, NodeProxy):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.__members__ = []

    def allowed(self, item):
        if item.kind in (CursorKind.ENUM_CONSTANT_DECL,):
            return True
        return super().allowed(item) 

    @property
    def dependencies(self) -> set[Record]:
        deps = OrderedSet()
        if self.parent and isinstance(self.parent, Record):
            deps.add(self.parent)
        return deps



class EnumConstant(NodeProxy):
    pass

class Variable(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class TypeAliasTemplateDecl(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            CursorKind.TEMPLATE_TYPE_PARAMETER,
            CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
        ):
            return self.check_parent(item)
        return super().allowed(item)

    pass


class TemplateTypeParam(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            # CursorKind.TEMPLATE_TYPE_PARAMETER,
            # CursorKind.TEMPLATE_NON_TYPE_PARAMETER,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class TemplateNonTypeParam(NodeProxy):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.ref_type = None

    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF,):
            if self.ref_type:
                return False
            return self.check_parent(item)
        return super().allowed(item)

    def accept(self, item):
        if super().accept(item):
            self.ref_type = item
            return True
        return False


class Constructor(Callable):
    pass


class Destructor(Callable):
    pass


FACTORY = {
    # CursorKind.ADDR_LABEL_EXPR,
    # CursorKind.ALIGNED_ATTR,
    # CursorKind.ANNOTATE_ATTR,
    # CursorKind.ARRAY_SUBSCRIPT_EXPR,
    # CursorKind.ASM_LABEL_ATTR,
    # CursorKind.ASM_STMT,
    # CursorKind.BINARY_OPERATOR,
    # CursorKind.BLOCK_EXPR,
    # CursorKind.BREAK_STMT,
    # CursorKind.CALL_EXPR,
    # CursorKind.CASE_STMT,
    # CursorKind.CHARACTER_LITERAL,
    CursorKind.CLASS_DECL: Class,
    CursorKind.CLASS_TEMPLATE: ClassTemplate,
    CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION: ClassTemplatePartialSpecialization,
    # CursorKind.COMPOUND_ASSIGNMENT_OPERATOR,
    # CursorKind.COMPOUND_LITERAL_EXPR,
    # CursorKind.COMPOUND_STMT,
    # CursorKind.CONDITIONAL_OPERATOR,
    CursorKind.CONSTRUCTOR: Constructor,
    # CursorKind.CONST_ATTR,
    # CursorKind.CONTINUE_STMT,
    # CursorKind.CONVERGENT_ATTR,
    # CursorKind.CONVERSION_FUNCTION,
    # CursorKind.CSTYLE_CAST_EXPR,
    # CursorKind.CUDACONSTANT_ATTR,
    # CursorKind.CUDADEVICE_ATTR,
    # CursorKind.CUDAGLOBAL_ATTR,
    # CursorKind.CUDAHOST_ATTR,
    # CursorKind.CUDASHARED_ATTR,
    # CursorKind.CXX_ACCESS_SPEC_DECL,
    CursorKind.CXX_BASE_SPECIFIER: BaseSpecifier,
    # CursorKind.CXX_BOOL_LITERAL_EXPR,
    # CursorKind.CXX_CATCH_STMT,
    # CursorKind.CXX_CONST_CAST_EXPR,
    # CursorKind.CXX_DELETE_EXPR,
    # CursorKind.CXX_DYNAMIC_CAST_EXPR,
    # CursorKind.CXX_FINAL_ATTR,
    # CursorKind.CXX_FOR_RANGE_STMT,
    # CursorKind.CXX_FUNCTIONAL_CAST_EXPR,
    CursorKind.CXX_METHOD: Method,
    # CursorKind.CXX_NEW_EXPR,
    # CursorKind.CXX_NULL_PTR_LITERAL_EXPR,
    # CursorKind.CXX_OVERRIDE_ATTR,
    # CursorKind.CXX_REINTERPRET_CAST_EXPR,
    # CursorKind.CXX_STATIC_CAST_EXPR,
    # CursorKind.CXX_THIS_EXPR,
    # CursorKind.CXX_THROW_EXPR,
    # CursorKind.CXX_TRY_STMT,
    # CursorKind.CXX_TYPEID_EXPR,
    # CursorKind.CXX_UNARY_EXPR,
    # CursorKind.DECL_REF_EXPR,
    # CursorKind.DECL_STMT,
    # CursorKind.DEFAULT_STMT,
    CursorKind.DESTRUCTOR: Destructor,
    # CursorKind.DLLEXPORT_ATTR,
    # CursorKind.DLLIMPORT_ATTR,
    # CursorKind.DO_STMT,
    CursorKind.ENUM_CONSTANT_DECL: EnumConstant,
    CursorKind.ENUM_DECL: Enum,
    CursorKind.FIELD_DECL: Field,
    # CursorKind.FLOATING_LITERAL,
    # CursorKind.FOR_STMT,
    # CursorKind.FRIEND_DECL,
    CursorKind.FUNCTION_DECL: Function,
    CursorKind.FUNCTION_TEMPLATE: FunctionTemplate,
    # CursorKind.GENERIC_SELECTION_EXPR,
    # CursorKind.GNU_NULL_EXPR,
    # CursorKind.GOTO_STMT,
    # CursorKind.IB_ACTION_ATTR,
    # CursorKind.IB_OUTLET_ATTR,
    # CursorKind.IB_OUTLET_COLLECTION_ATTR,
    # CursorKind.IF_STMT,
    # CursorKind.IMAGINARY_LITERAL,
    # CursorKind.INCLUSION_DIRECTIVE,
    # CursorKind.INDIRECT_GOTO_STMT,
    # CursorKind.INIT_LIST_EXPR,
    # CursorKind.INTEGER_LITERAL,
    # CursorKind.INVALID_CODE,
    # CursorKind.INVALID_FILE,
    # CursorKind.LABEL_REF,
    # CursorKind.LABEL_STMT,
    # CursorKind.LAMBDA_EXPR,
    # CursorKind.LINKAGE_SPEC,
    # CursorKind.MACRO_DEFINITION,
    # CursorKind.MACRO_INSTANTIATION,
    # CursorKind.MEMBER_REF,
    # CursorKind.MEMBER_REF_EXPR,
    # CursorKind.MODULE_IMPORT_DECL,
    # CursorKind.MS_ASM_STMT,
    CursorKind.NAMESPACE: Namespace,
    # CursorKind.NAMESPACE_ALIAS,
    # CursorKind.NAMESPACE_REF,
    # CursorKind.NODUPLICATE_ATTR,
    # CursorKind.NOT_IMPLEMENTED,
    # CursorKind.NO_DECL_FOUND,
    # CursorKind.NULL_STMT,
    # CursorKind.OBJC_AT_CATCH_STMT,
    # CursorKind.OBJC_AT_FINALLY_STMT,
    # CursorKind.OBJC_AT_SYNCHRONIZED_STMT,
    # CursorKind.OBJC_AT_THROW_STMT,
    # CursorKind.OBJC_AT_TRY_STMT,
    # CursorKind.OBJC_AUTORELEASE_POOL_STMT,
    # CursorKind.OBJC_AVAILABILITY_CHECK_EXPR,
    # CursorKind.OBJC_BRIDGE_CAST_EXPR,
    # CursorKind.OBJC_CATEGORY_DECL,
    # CursorKind.OBJC_CATEGORY_IMPL_DECL,
    # CursorKind.OBJC_CLASS_METHOD_DECL,
    # CursorKind.OBJC_CLASS_REF,
    # CursorKind.OBJC_DYNAMIC_DECL,
    # CursorKind.OBJC_ENCODE_EXPR,
    # CursorKind.OBJC_FOR_COLLECTION_STMT,
    # CursorKind.OBJC_IMPLEMENTATION_DECL,
    # CursorKind.OBJC_INSTANCE_METHOD_DECL,
    # CursorKind.OBJC_INTERFACE_DECL,
    # CursorKind.OBJC_IVAR_DECL,
    # CursorKind.OBJC_MESSAGE_EXPR,
    # CursorKind.OBJC_PROPERTY_DECL,
    # CursorKind.OBJC_PROTOCOL_DECL,
    # CursorKind.OBJC_PROTOCOL_EXPR,
    # CursorKind.OBJC_PROTOCOL_REF,
    # CursorKind.OBJC_SELECTOR_EXPR,
    # CursorKind.OBJC_STRING_LITERAL,
    # CursorKind.OBJC_SUPER_CLASS_REF,
    # CursorKind.OBJC_SYNTHESIZE_DECL,
    # CursorKind.OBJ_BOOL_LITERAL_EXPR,
    # CursorKind.OBJ_SELF_EXPR,
    # CursorKind.OMP_ARRAY_SECTION_EXPR,
    # CursorKind.OMP_ATOMIC_DIRECTIVE,
    # CursorKind.OMP_BARRIER_DIRECTIVE,
    # CursorKind.OMP_CANCELLATION_POINT_DIRECTIVE,
    # CursorKind.OMP_CANCEL_DIRECTIVE,
    # CursorKind.OMP_CRITICAL_DIRECTIVE,
    # CursorKind.OMP_DISTRIBUTE_DIRECTIVE,
    # CursorKind.OMP_DISTRIBUTE_PARALLELFOR_DIRECTIVE,
    # CursorKind.OMP_DISTRIBUTE_PARALLEL_FOR_SIMD_DIRECTIVE,
    # CursorKind.OMP_DISTRIBUTE_SIMD_DIRECTIVE,
    # CursorKind.OMP_FLUSH_DIRECTIVE,
    # CursorKind.OMP_FOR_DIRECTIVE,
    # CursorKind.OMP_FOR_SIMD_DIRECTIVE,
    # CursorKind.OMP_MASTER_DIRECTIVE,
    # CursorKind.OMP_ORDERED_DIRECTIVE,
    # CursorKind.OMP_PARALLELFORSIMD_DIRECTIVE,
    # CursorKind.OMP_PARALLEL_DIRECTIVE,
    # CursorKind.OMP_PARALLEL_FOR_DIRECTIVE,
    # CursorKind.OMP_PARALLEL_SECTIONS_DIRECTIVE,
    # CursorKind.OMP_SECTIONS_DIRECTIVE,
    # CursorKind.OMP_SECTION_DIRECTIVE,
    # CursorKind.OMP_SIMD_DIRECTIVE,
    # CursorKind.OMP_SINGLE_DIRECTIVE,
    # CursorKind.OMP_TARGET_DATA_DIRECTIVE,
    # CursorKind.OMP_TARGET_DIRECTIVE,
    # CursorKind.OMP_TARGET_ENTER_DATA_DIRECTIVE,
    # CursorKind.OMP_TARGET_EXIT_DATA_DIRECTIVE,
    # CursorKind.OMP_TARGET_PARALLELFOR_DIRECTIVE,
    # CursorKind.OMP_TARGET_PARALLEL_DIRECTIVE,
    # CursorKind.OMP_TARGET_PARALLEL_FOR_SIMD_DIRECTIVE,
    # CursorKind.OMP_TARGET_SIMD_DIRECTIVE,
    # CursorKind.OMP_TARGET_UPDATE_DIRECTIVE,
    # CursorKind.OMP_TASKGROUP_DIRECTIVE,
    # CursorKind.OMP_TASKWAIT_DIRECTIVE,
    # CursorKind.OMP_TASKYIELD_DIRECTIVE,
    # CursorKind.OMP_TASK_DIRECTIVE,
    # CursorKind.OMP_TASK_LOOP_DIRECTIVE,
    # CursorKind.OMP_TASK_LOOP_SIMD_DIRECTIVE,
    # CursorKind.OMP_TEAMS_DIRECTIVE,
    # CursorKind.OMP_TEAMS_DISTRIBUTE_DIRECTIVE,
    # CursorKind.OVERLOADED_DECL_REF,
    # CursorKind.OVERLOAD_CANDIDATE,
    # CursorKind.PACKED_ATTR,
    # CursorKind.PACK_EXPANSION_EXPR,
    # CursorKind.PAREN_EXPR,
    CursorKind.PARM_DECL: Param,
    # CursorKind.PREPROCESSING_DIRECTIVE,
    # CursorKind.PURE_ATTR,
    # CursorKind.RETURN_STMT,
    # CursorKind.SEH_EXCEPT_STMT,
    # CursorKind.SEH_FINALLY_STMT,
    # CursorKind.SEH_LEAVE_STMT,
    # CursorKind.SEH_TRY_STMT,
    # CursorKind.SIZE_OF_PACK_EXPR,
    # CursorKind.STATIC_ASSERT,
    # CursorKind.STRING_LITERAL,
    CursorKind.STRUCT_DECL: Struct,
    # CursorKind.SWITCH_STMT,
    # "StmtExpr",
    CursorKind.TEMPLATE_NON_TYPE_PARAMETER: TemplateNonTypeParam,
    CursorKind.TEMPLATE_REF: TemplateRef,
    # CursorKind.TEMPLATE_TEMPLATE_PARAMETER,
    CursorKind.TEMPLATE_TYPE_PARAMETER: TemplateTypeParam,
    CursorKind.TRANSLATION_UNIT: TxUnit,
    CursorKind.TYPEDEF_DECL: TypeDef,
    CursorKind.TYPE_ALIAS_DECL: TypeAliasDecl,
    CursorKind.TYPE_ALIAS_TEMPLATE_DECL: TypeAliasTemplateDecl,
    CursorKind.TYPE_REF: TypeRef,
    # CursorKind.UNARY_OPERATOR,
    # CursorKind.UNEXPOSED_ATTR,
    CursorKind.UNEXPOSED_DECL: Pop,
    # CursorKind.UNEXPOSED_EXPR,
    # CursorKind.UNEXPOSED_STMT,
    # CursorKind.UNION_DECL,
    # CursorKind.USING_DECLARATION,
    # CursorKind.USING_DIRECTIVE,
    # CursorKind.VARIABLE_REF,
    CursorKind.VAR_DECL: Variable,
    # CursorKind.VISIBILITY_ATTR,
    # CursorKind.WARN_UNUSED_ATTR,
    # CursorKind.WARN_UNUSED_RESULT_ATTR,
    # CursorKind.WHILE_STMT,
}
