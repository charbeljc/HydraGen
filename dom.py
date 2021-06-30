from __future__ import annotations
import sys
import typing
from binder import NamedContainer
from clang.cindex import Index, CursorKind, Cursor, AccessSpecifier, TranslationUnit
from logzero import logger
from orderedset import OrderedSet


def kind(node):
    return (
        ("%s:%r" % (node.kind, node.spelling))[len("CursorKind.") :] if node else None
    )


class Config:
    pass


class Context:
    def __init__(self, factory: dict[CursorKind,type], config: Config):
        self.factory = factory
        self.config = config
        self.elements = {}
        self.stack = []
        self.flags = []
        self.index = Index.create()

    def set_flags(self, flags: str | list[str]):
        if isinstance(flags, str):
            self.flags = flags.strip().split()
        else:
            self.flags = flags[:]

    def add_flag(self, flag: str):
        flag = flag.strip()
        self.flags.append(flag)

    def parse(self, path) -> TxUnit:
        tu = self.index.parse(
            path,
            self.flags,
            options=TranslationUnit.PARSE_INCOMPLETE
            | TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
        )
        for diag in tu.diagnostics:
            print(diag, file=sys.stderr)
        return typing.cast(TxUnit, self.make(tu.cursor))

    def push(self, node: NodeProxy):
        self.stack.append(node)

    def pop(self, node: NodeProxy):
        check = self.stack.pop()
        assert node is check

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
                obj = self.factory[node.kind](self, node)
        return obj


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
            logger.warning(
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

    def allowed(self, item):
        return False

    def check_parent(self, item):
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
            logger.debug("%s not parent of %s", self, item)
            return False
        return True

    def walk(self, node=None):
        if node is None:
            node = self.node
        else:
            if self.node.kind != node.kind:
                logger.warning(
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
                obj.walk(child)
        self.context.pop(self)
        return self

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


class Namespace(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.FUNCTION_DECL,
            CursorKind.FUNCTION_TEMPLATE,
            CursorKind.STRUCT_DECL,
            CursorKind.CLASS_DECL,
            CursorKind.CLASS_TEMPLATE,
            CursorKind.NAMESPACE,
            CursorKind.TYPEDEF_DECL,
            CursorKind.TYPE_ALIAS_TEMPLATE_DECL,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class Callable(NodeProxy):
    def __init__(self, context, node, parent=None):
        super().__init__(context, node, parent)
        self.inline = False
        self.overloads = []
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
    def return_type(self) -> NodeProxy | None:
        return None


class Function(Callable):
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
    pass


class Param(NodeProxy):
    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            return self.check_parent(item)
        return super().allowed(item)


class Field(NodeProxy):
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
            CursorKind.TYPEDEF_DECL,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class BaseSpecifier(NodeProxy):
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
        ):
            return self.check_parent(item)
        return super().allowed(item)

    @property
    def bases(self) -> list[BaseSpecifier]:
        if self._bases is None:
            self._bases = list(self._filter(BaseSpecifier))
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


class Class(Record):
    def allowed(self, item):
        if item.kind in (
            CursorKind.CLASS_DECL,
            CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
        ):
            return self.check_parent(item)
        return super().allowed(item)


class Struct(Record):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TYPEDEF_DECL,
            CursorKind.FUNCTION_TEMPLATE,
        ):
            return self.check_parent(item)
        return super().allowed(item)


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
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            return self.check_parent(item)
        return super().allowed(item)


class TypeAliasDecl(NodeProxy):
    def allowed(self, item):
        if item.kind in (CursorKind.TYPE_REF, CursorKind.TEMPLATE_REF):
            return self.check_parent(item)
        return super().allowed(item)

    pass


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


class Enum(NodeProxy):
    def __init__(self, name, node, parent=None):
        super().__init__(name, node, parent)
        self.__members__ = []

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


class TypeRef(NodeProxy):
    pass


class TemplateRef(NodeProxy):
    def allowed(self, item):
        if item.kind in (
            CursorKind.TYPE_REF,
            CursorKind.TEMPLATE_REF,
            CursorKind.TYPE_ALIAS_DECL,
        ):
            return self.check_parent(item)
        return super().allowed(item)


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
    # CursorKind.ENUM_CONSTANT_DECL,
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
