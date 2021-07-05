from __future__ import annotations
from logging import StreamHandler

import sys
from collections import abc
import typing

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

from .conf import Config


def kind(node):
    return (
        ("%s:%r" % (node.kind, node.spelling))[len("CursorKind.") :] if node else None
    )


class Context:

    factory: dict[CursorKind, abc.Callable[[Context, Cursor], NodeProxy | None]]
    config: Config
    elements: dict[str, NodeProxy]  # key is clang node's usr
    builtins: dict[str, NodeProxy]
    _casters: dict[NodeProxy, NodeProxy] | None
    _tx: TxUnit | None

    def __init__(self, factory: dict[CursorKind, type], config: Config):
        self.factory = factory
        self.config = config
        self.elements = {}
        self.builtins = {}
        self.stack = []
        self.index = Index.create()
        self._casters = None

    def parse(self, path) -> tuple[TxUnit, list[Include]]:
        tu = self.index.parse(
            path,
            self.config.cflags + ["-I%s" % path for path in self.config.include_path],
            options=TranslationUnit.PARSE_INCOMPLETE
            | TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
        )
        for diag in tu.diagnostics:
            print(diag, file=sys.stderr)
        includes = [Include(inc) for inc in tu.get_includes()]
        self._tx = typing.cast(TxUnit, self.make(tu.cursor))
        return self._tx, includes

    def casters(self):
        if self._casters is None:
            _casters = {}
            if not self._tx:
                return {}
            #casting = self._tx["pybind11::detail::type_caster"]
            #breakpoint()
            for casting in self._tx["pybind11::detail::type_caster"]:
                tref = list(casting._filter(TypeRef))
                if tref:
                    _casters[tref[0].type] = casting
            self._casters = _casters
        return self._casters

    def push(self, node: NodeProxy):
        self.stack.append(node)
        return self

    def pop(self, node: NodeProxy):
        check = self.stack.pop()
        assert node is check
        return self

    def indent(self) -> str:
        return " " * len(self.stack)

    def is_banned(self, item: NodeProxy) -> bool:
        if self.config.is_banned(item.fullname):
            return True
        elif isinstance(item, Callable):
            key = f"{item.fullname}({item.cpp_signature})"
            return self.config.is_banned(key)
        return False


    def bind_with_lambda(self, item: Callable) -> str | None:
        if not item.parent:
            return None
        candidate = self.config._lambdas.get(item.parent.fullname)
        if candidate: 
            return candidate.get(item.displayname)
        return None

    def get_addon_methods(self, item: Record) -> list[tuple[str,str]]:
        candidate = self.config._addon_methods.get(item.fullname)
        if not candidate:
            return []
        else:
            return list(candidate.items())

    def export_enum_values(self, item: Enum) -> bool:
        return self.config.are_enum_values_exported(item.fullname)

    def lambda_code(self, item: NodeProxy) -> str:
        breakpoint()
        return ''

    def return_policy(self, item: Callable) -> str | None:
        candidate = self.config._policies.get(item.fullname)
        if not candidate:
            key = item.fullname + '(' + item.cpp_signature + ')'
            candidate = self.config._policies.get(key)
        return candidate

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
                    obj = self.factory[node.kind](self, node)
                    if obj:
                        self.elements[usr] = obj
                    else:
                        logger.debug("skip: %s %s", node.kind, node.spelling)
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


class NodeProxy:
    name: str
    node: Cursor
    context: Context
    parent: NodeProxy | None
    content: dict

    def __init__(self, context: Context, node: Cursor, parent: NodeProxy | None = None):
        self.context = context
        self.name = node.spelling # or node.get_usr()
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
            real_parent = self.context.elements.get(item.node.semantic_parent.get_usr())
        else:
            real_parent = self
        if not real_parent:
            logger.warning("XXX rpnf: %s, %s %s:\n%s",
            item, item.node.semantic_parent.kind, item.node.semantic_parent.spelling, item.location) 
            return False
        if real_parent is self or isinstance(real_parent, ClassTemplate):
            logger.debug("ACCEPT: %s, item %s, loc: %s", real_parent, item, item.location)
            real_parent.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(real_parent, TxUnit):
                item.parent = real_parent
        elif isinstance(item, TypeAliasTemplateDecl) and isinstance(real_parent, (Namespace, Record)):
            logger.debug("ACCEPT: %s, item %s, loc: %s", real_parent, item, item.location)
            real_parent.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(real_parent, TxUnit):
                item.parent = real_parent
        elif isinstance(item, (Constructor, Destructor, Method)) and isinstance(real_parent, Record):
            logger.debug("ACCEPT: %s, item %s, loc: %s", real_parent, item, item.location)
            real_parent.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(real_parent, TxUnit):
                item.parent = real_parent
        elif (isinstance(item, (Enum, Struct)) and isinstance(self, TypeDef)
            or isinstance(item, (Enum, Struct)) and isinstance(self, Field) and isinstance(real_parent, Record)):
            # small deviation
            logger.warning("TypeDef/Field Enum/Struct: %s, %s, %s: %s", item, self, real_parent, item.location)
            logger.debug("ACCEPT(*): %s, item %s, loc: %s", self, item, item.location)
            self.content.setdefault(item.name, OrderedSet()).add(item)
            real_parent.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(real_parent, TxUnit):
                item.parent = real_parent
        elif isinstance(self, (TxUnit, Namespace)) and isinstance(real_parent, (Namespace, Record)):
            logger.debug("ACCEPT: %s, item %s, loc: %s", real_parent, item, item.location)
            real_parent.content.setdefault(item.name, OrderedSet()).add(item)
            if not isinstance(real_parent, TxUnit):
                item.parent = real_parent

        else:
            logger.warning("reject: self: %s item: %s, real_parent: %s\nloc: %s", 
                self, item, real_parent, item.location)
            return False
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
            # logger.warn("%s not parent of %s (%s)", self, item, item_parent.kind)
            return True # False
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
                if not ok:
                    logger.debug("reject! %s, self: %s", obj, self)
                obj.walk(child)
            else:
                #logger.warning("abort!! %s %r", child.kind, child.spelling)
                pass
        self.context.pop(self)
        return self

    def is_builtin(self):
        return False

    def is_abstract(self):
        return False

    @property
    def namespaces(self):
        return {n.name: n for n in list(self._filter(Namespace))}

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

    def __getitem__(self, name_or_path) -> NodeProxy:
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
        if isinstance(types, list):
            types = tuple(types)
        if not predicate:
            predicate = lambda _: True
        for objs in self.content.values():
            for obj in objs:
                if isinstance(obj, types) and predicate(obj):
                    yield obj

    @property
    def dependencies(self) -> set[NodeProxy]:
        return OrderedSet()


class Bindable(NodeProxy):
    def bind(self, binder: Binder):
        binder.bind(self)

    def is_bindable(self):
        return True


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
        """This sucks ..."""
        node = None
        t = self._get_clang_type()
        assert not t or t.kind != TypeKind.INVALID
        type_ref = list(self._filter([TypeRef, TemplateRef]))
        if type_ref:
            if len(type_ref) != 1:
                logger.debug(
                    "mutiple typerefs: %s: assuming last is return type: %s",
                    self,
                    type_ref,
                )
            type_ref = type_ref[-1]
            decl = type_ref.node.get_definition()
            if decl:
                try:
                    node = self.context.elements[decl.get_usr()]
                except KeyError:
                    logger.warn("lookup failed: decl: %s %s", decl.kind, decl.spelling)
        else:
            assert t
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
                        logger.debug(
                            "lookup failed(def): %s %s %s",
                            defi.kind,
                            defi.spelling,
                            defi.get_usr(),
                        )
                else:
                    try:
                        node = self.context.elements[decl.get_usr()]
                    except KeyError:
                        logger.debug(
                            "lookup failed(decl): %s %s %s",
                            decl.kind,
                            decl.spelling,
                            decl.get_usr(),
                        )

        if not node:
            logger.debug("_compute_type() failed for %s", self)
        return node

    @property
    def type(self) -> NodeProxy:
        if self.type_ is None:
            self.type_ = self._compute_type()
        # assert self.type_ is not None
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

    def _get_clang_type(self) -> Type:
        return self.node.get_definition().type
    @property
    def dependencies(self):
        deps = OrderedSet()
        if self.type:
            deps.add(self.type)
            deps |= self.type.dependencies
        else:
            logger.warning("No Type for %s", self)
        return deps


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
        try:
            type_ref, *tail = self._filter((TypeRef, TemplateRef))
        except ValueError:
            breakpoint()
        else:
            if tail:
                logger.debug("BaseSpecifier: template? %s %s", type_ref, tail)
            if type_ref.node.type.kind == TypeKind.INVALID:
                logger.warning("BaseSpec: %s", self)
                return None
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
        self._records = None
        self._enums = None

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
            CursorKind.STRUCT_DECL,
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
                if node:
                    bases.append(node)
                else:
                    logger.warning("base-spec, missing type: %s", spec)
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
    def records(self) -> list[Record]:
        if self._records is None:
            self._records = list(self._filter(Record))
        return self._records

    @property
    def enums(self) -> list[Enum]:
        if self._enums is None:
            self._enums = list(self._filter(Enum))
        return self._enums
    @property
    def dependencies(self) -> set[Record]:
        deps = OrderedSet()
        if self.parent and isinstance(self.parent, Record):
            deps.add(self.parent)
        for base in self.bases:
            if base is not self:
                deps.add(base)
            else:
                logger.warning("Hu... %s", self)
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


class TypeDef(TypeHolder):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            CursorKind.ENUM_DECL,
        ):
            return self.check_parent(item)
        return super().allowed(item)

    def _get_clang_type(self) -> Type:
        return self.node.type.get_canonical()

    def is_builtin(self):
        return self.type and self.type.is_builtin()

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
    # CursorKind.UNEXPOSED_DECL: Pop,
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
