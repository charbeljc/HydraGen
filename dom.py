from clang.cindex import CursorKind
from logzero import logger

class NamedContainer:
    def __init__(self, name, node, parent=None):
        self.name = name
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
        return f"<{self.__class__.__name__} {self.name!r}>" # {self.usr!r}>"

    def accept(self, item):
        logger.debug("ACCEPT: %s, %s", self, item)
        if item.name in self.content:
            self.content[item.name].add(item)
        else:
            self.content[item.name] = set(item)

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

class TemplateNonTypeParam(NamedContainer):
    pass


class TxUnit(NamedContainer):
    pass

class Constructor(NamedContainer):
    pass
class Destructor(NamedContainer):
    pass
class BaseSpecifier(NamedContainer):
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
    CursorKind.CLASS_DECL : Class,
    CursorKind.CLASS_TEMPLATE : ClassTemplate,
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
    CursorKind.STRUCT_DECL : Struct,
    # CursorKind.SWITCH_STMT,
    # "StmtExpr",
    CursorKind.TEMPLATE_NON_TYPE_PARAMETER: TemplateNonTypeParam,
    # CursorKind.TEMPLATE_REF,
    # CursorKind.TEMPLATE_TEMPLATE_PARAMETER,
    CursorKind.TEMPLATE_TYPE_PARAMETER: TemplateTypeParam,
    CursorKind.TRANSLATION_UNIT: TxUnit,
    CursorKind.TYPEDEF_DECL: TypeDef,
    # CursorKind.TYPE_ALIAS_DECL,
    # CursorKind.TYPE_ALIAS_TEMPLATE_DECL,
    CursorKind.TYPE_REF: TypeRef,
    # CursorKind.UNARY_OPERATOR,
    # CursorKind.UNEXPOSED_ATTR,
    # CursorKind.UNEXPOSED_DECL,
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
