from ctypes import *
from typing import Any

class c_interop_string(c_char_p):
    def __init__(self, p: Any | None = ...) -> None: ...
    @property
    def value(self): ...
    @classmethod
    def from_param(cls, param): ...
    @staticmethod
    def to_python_string(x, *args): ...

class TranslationUnitLoadError(Exception): ...

class TranslationUnitSaveError(Exception):
    ERROR_UNKNOWN: int
    ERROR_TRANSLATION_ERRORS: int
    ERROR_INVALID_TU: int
    save_error: Any
    def __init__(self, enumeration, message) -> None: ...

class CachedProperty:
    wrapped: Any
    __doc__: Any
    def __init__(self, wrapped) -> None: ...
    def __get__(self, instance, instance_type: Any | None = ...): ...

class _CXString(Structure):
    def __del__(self) -> None: ...
    @staticmethod
    def from_result(res, fn: Any | None = ..., args: Any | None = ...): ...

class SourceLocation(Structure):
    @staticmethod
    def from_position(tu, file, line, column): ...
    @staticmethod
    def from_offset(tu, file, offset): ...
    @property
    def file(self): ...
    @property
    def line(self): ...
    @property
    def column(self): ...
    @property
    def offset(self): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...

class SourceRange(Structure):
    @staticmethod
    def from_locations(start, end): ...
    @property
    def start(self): ...
    @property
    def end(self): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
    def __contains__(self, other): ...

class Diagnostic:
    Ignored: int
    Note: int
    Warning: int
    Error: int
    Fatal: int
    DisplaySourceLocation: int
    DisplayColumn: int
    DisplaySourceRanges: int
    DisplayOption: int
    DisplayCategoryId: int
    DisplayCategoryName: int
    ptr: Any
    def __init__(self, ptr) -> None: ...
    def __del__(self) -> None: ...
    @property
    def severity(self): ...
    @property
    def location(self): ...
    @property
    def spelling(self): ...
    diag: Any
    @property
    def ranges(self): ...
    @property
    def fixits(self): ...
    diag_set: Any
    @property
    def children(self): ...
    @property
    def category_number(self): ...
    @property
    def category_name(self): ...
    @property
    def option(self): ...
    @property
    def disable_option(self): ...
    def format(self, options: Any | None = ...): ...
    def from_param(self): ...

class FixIt:
    range: Any
    value: Any
    def __init__(self, range, value) -> None: ...

class TokenGroup:
    def __init__(self, tu, memory, count) -> None: ...
    def __del__(self) -> None: ...
    @staticmethod
    def get_tokens(tu, extent) -> None: ...

class TokenKind:
    value: Any
    name: Any
    def __init__(self, value, name) -> None: ...
    @staticmethod
    def from_value(value): ...
    @staticmethod
    def register(value, name) -> None: ...

class BaseEnumeration:
    value: Any
    def __init__(self, value) -> None: ...
    def from_param(self): ...
    @property
    def name(self): ...
    @classmethod
    def from_id(cls, id): ...

class CursorKind(BaseEnumeration):
    @staticmethod
    def get_all_kinds(): ...
    def is_declaration(self): ...
    def is_reference(self): ...
    def is_expression(self): ...
    def is_statement(self): ...
    def is_attribute(self): ...
    def is_invalid(self): ...
    def is_translation_unit(self): ...
    def is_preprocessing(self): ...
    def is_unexposed(self): ...
    UNEXPOSED_DECL = ...
    STRUCT_DECL = ...
    UNION_DECL = ...
    CLASS_DECL = ...
    ENUM_DECL = ...
    FIELD_DECL = ...
    ENUM_CONSTANT_DECL = ...
    FUNCTION_DECL = ...
    VAR_DECL = ...
    PARM_DECL = ...
    OBJC_INTERFACE_DECL = ...
    OBJC_CATEGORY_DECL = ...
    OBJC_PROTOCOL_DECL = ...
    OBJC_PROPERTY_DECL = ...
    OBJC_IVAR_DECL = ...
    OBJC_INSTANCE_METHOD_DECL = ...
    OBJC_CLASS_METHOD_DECL = ...
    OBJC_IMPLEMENTATION_DECL = ...
    OBJC_CATEGORY_IMPL_DECL = ...
    TYPEDEF_DECL = ...
    CXX_METHOD = ...
    NAMESPACE = ...
    LINKAGE_SPEC = ...
    CONSTRUCTOR = ...
    DESTRUCTOR = ...
    CONVERSION_FUNCTION = ...
    TEMPLATE_TYPE_PARAMETER = ...
    TEMPLATE_NON_TYPE_PARAMETER = ...
    TEMPLATE_TEMPLATE_PARAMETER = ...
    FUNCTION_TEMPLATE = ...
    CLASS_TEMPLATE = ...
    CLASS_TEMPLATE_PARTIAL_SPECIALIZATION = ...
    NAMESPACE_ALIAS = ...
    USING_DIRECTIVE = ...
    USING_DECLARATION = ...
    TYPE_ALIAS_DECL = ...
    OBJC_SYNTHESIZE_DECL = ...
    OBJC_DYNAMIC_DECL = ...
    CXX_ACCESS_SPEC_DECL = ...
    OBJC_SUPER_CLASS_REF = ...
    OBJC_PROTOCOL_REF = ...
    OBJC_CLASS_REF = ...
    TYPE_REF = ...
    CXX_BASE_SPECIFIER = ...
    TEMPLATE_REF = ...
    NAMESPACE_REF = ...
    MEMBER_REF = ...
    LABEL_REF = ...
    OVERLOADED_DECL_REF = ...
    VARIABLE_REF = ...
    INVALID_FILE = ...
    NO_DECL_FOUND = ...
    NOT_IMPLEMENTED = ...
    INVALID_CODE = ...
    UNEXPOSED_EXPR = ...
    DECL_REF_EXPR = ...
    MEMBER_REF_EXPR = ...
    CALL_EXPR = ...
    OBJC_MESSAGE_EXPR = ...
    BLOCK_EXPR = ...
    INTEGER_LITERAL = ...
    FLOATING_LITERAL = ...
    IMAGINARY_LITERAL = ...
    STRING_LITERAL = ...
    CHARACTER_LITERAL = ...
    PAREN_EXPR = ...
    UNARY_OPERATOR = ...
    ARRAY_SUBSCRIPT_EXPR = ...
    BINARY_OPERATOR = ...
    COMPOUND_ASSIGNMENT_OPERATOR = ...
    CONDITIONAL_OPERATOR = ...
    CSTYLE_CAST_EXPR = ...
    COMPOUND_LITERAL_EXPR = ...
    INIT_LIST_EXPR = ...
    ADDR_LABEL_EXPR = ...
    StmtExpr = ...
    GENERIC_SELECTION_EXPR = ...
    GNU_NULL_EXPR = ...
    CXX_STATIC_CAST_EXPR = ...
    CXX_DYNAMIC_CAST_EXPR = ...
    CXX_REINTERPRET_CAST_EXPR = ...
    CXX_CONST_CAST_EXPR = ...
    CXX_FUNCTIONAL_CAST_EXPR = ...
    CXX_TYPEID_EXPR = ...
    CXX_BOOL_LITERAL_EXPR = ...
    CXX_NULL_PTR_LITERAL_EXPR = ...
    CXX_THIS_EXPR = ...
    CXX_THROW_EXPR = ...
    CXX_NEW_EXPR = ...
    CXX_DELETE_EXPR = ...
    CXX_UNARY_EXPR = ...
    OBJC_STRING_LITERAL = ...
    OBJC_ENCODE_EXPR = ...
    OBJC_SELECTOR_EXPR = ...
    OBJC_PROTOCOL_EXPR = ...
    OBJC_BRIDGE_CAST_EXPR = ...
    PACK_EXPANSION_EXPR = ...
    SIZE_OF_PACK_EXPR = ...
    LAMBDA_EXPR = ...
    OBJ_BOOL_LITERAL_EXPR = ...
    OBJ_SELF_EXPR = ...
    OMP_ARRAY_SECTION_EXPR = ...
    OBJC_AVAILABILITY_CHECK_EXPR = ...
    UNEXPOSED_STMT = ...
    LABEL_STMT = ...
    COMPOUND_STMT = ...
    CASE_STMT = ...
    DEFAULT_STMT = ...
    IF_STMT = ...
    SWITCH_STMT = ...
    WHILE_STMT = ...
    DO_STMT = ...
    FOR_STMT = ...
    GOTO_STMT = ...
    INDIRECT_GOTO_STMT = ...
    CONTINUE_STMT = ...
    BREAK_STMT = ...
    RETURN_STMT = ...
    ASM_STMT = ...
    OBJC_AT_TRY_STMT = ...
    OBJC_AT_CATCH_STMT = ...
    OBJC_AT_FINALLY_STMT = ...
    OBJC_AT_THROW_STMT = ...
    OBJC_AT_SYNCHRONIZED_STMT = ...
    OBJC_AUTORELEASE_POOL_STMT = ...
    OBJC_FOR_COLLECTION_STMT = ...
    CXX_CATCH_STMT = ...
    CXX_TRY_STMT = ...
    CXX_FOR_RANGE_STMT = ...
    SEH_TRY_STMT = ...
    SEH_EXCEPT_STMT = ...
    SEH_FINALLY_STMT = ...
    MS_ASM_STMT = ...
    NULL_STMT = ...
    DECL_STMT = ...
    OMP_PARALLEL_DIRECTIVE = ...
    OMP_SIMD_DIRECTIVE = ...
    OMP_FOR_DIRECTIVE = ...
    OMP_SECTIONS_DIRECTIVE = ...
    OMP_SECTION_DIRECTIVE = ...
    OMP_SINGLE_DIRECTIVE = ...
    OMP_PARALLEL_FOR_DIRECTIVE = ...
    OMP_PARALLEL_SECTIONS_DIRECTIVE = ...
    OMP_TASK_DIRECTIVE = ...
    OMP_MASTER_DIRECTIVE = ...
    OMP_CRITICAL_DIRECTIVE = ...
    OMP_TASKYIELD_DIRECTIVE = ...
    OMP_BARRIER_DIRECTIVE = ...
    OMP_TASKWAIT_DIRECTIVE = ...
    OMP_FLUSH_DIRECTIVE = ...
    SEH_LEAVE_STMT = ...
    OMP_ORDERED_DIRECTIVE = ...
    OMP_ATOMIC_DIRECTIVE = ...
    OMP_FOR_SIMD_DIRECTIVE = ...
    OMP_PARALLELFORSIMD_DIRECTIVE = ...
    OMP_TARGET_DIRECTIVE = ...
    OMP_TEAMS_DIRECTIVE = ...
    OMP_TASKGROUP_DIRECTIVE = ...
    OMP_CANCELLATION_POINT_DIRECTIVE = ...
    OMP_CANCEL_DIRECTIVE = ...
    OMP_TARGET_DATA_DIRECTIVE = ...
    OMP_TASK_LOOP_DIRECTIVE = ...
    OMP_TASK_LOOP_SIMD_DIRECTIVE = ...
    OMP_DISTRIBUTE_DIRECTIVE = ...
    OMP_TARGET_ENTER_DATA_DIRECTIVE = ...
    OMP_TARGET_EXIT_DATA_DIRECTIVE = ...
    OMP_TARGET_PARALLEL_DIRECTIVE = ...
    OMP_TARGET_PARALLELFOR_DIRECTIVE = ...
    OMP_TARGET_UPDATE_DIRECTIVE = ...
    OMP_DISTRIBUTE_PARALLELFOR_DIRECTIVE = ...
    OMP_DISTRIBUTE_PARALLEL_FOR_SIMD_DIRECTIVE = ...
    OMP_DISTRIBUTE_SIMD_DIRECTIVE = ...
    OMP_TARGET_PARALLEL_FOR_SIMD_DIRECTIVE = ...
    OMP_TARGET_SIMD_DIRECTIVE = ...
    OMP_TEAMS_DISTRIBUTE_DIRECTIVE = ...
    TRANSLATION_UNIT = ...
    UNEXPOSED_ATTR = ...
    IB_ACTION_ATTR = ...
    IB_OUTLET_ATTR = ...
    IB_OUTLET_COLLECTION_ATTR = ...
    CXX_FINAL_ATTR = ...
    CXX_OVERRIDE_ATTR = ...
    ANNOTATE_ATTR = ...
    ASM_LABEL_ATTR = ...
    PACKED_ATTR = ...
    PURE_ATTR = ...
    CONST_ATTR = ...
    NODUPLICATE_ATTR = ...
    CUDACONSTANT_ATTR = ...
    CUDADEVICE_ATTR = ...
    CUDAGLOBAL_ATTR = ...
    CUDAHOST_ATTR = ...
    CUDASHARED_ATTR = ...
    VISIBILITY_ATTR = ...
    DLLEXPORT_ATTR = ...
    DLLIMPORT_ATTR = ...
    CONVERGENT_ATTR = ...
    WARN_UNUSED_ATTR = ...
    WARN_UNUSED_RESULT_ATTR = ...
    ALIGNED_ATTR = ...
    PREPROCESSING_DIRECTIVE = ...
    MACRO_DEFINITION = ...
    MACRO_INSTANTIATION = ...
    INCLUSION_DIRECTIVE = ...
    MODULE_IMPORT_DECL = ...
    TYPE_ALIAS_TEMPLATE_DECL = ...
    STATIC_ASSERT = ...
    FRIEND_DECL = ...
    OVERLOAD_CANDIDATE = ...

class TemplateArgumentKind(BaseEnumeration): ...
class ExceptionSpecificationKind(BaseEnumeration): ...

class Cursor(Structure):
    @staticmethod
    def from_location(tu, location): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
    def is_definition(self): ...
    def is_const_method(self): ...
    def is_converting_constructor(self): ...
    def is_copy_constructor(self): ...
    def is_default_constructor(self): ...
    def is_move_constructor(self): ...
    def is_default_method(self): ...
    def is_mutable_field(self): ...
    def is_pure_virtual_method(self): ...
    def is_static_method(self): ...
    def is_virtual_method(self): ...
    def is_abstract_record(self): ...
    def is_scoped_enum(self): ...
    def get_definition(self): ...
    def get_usr(self): ...
    def get_included_file(self): ...
    @property
    def kind(self): ...
    @property
    def spelling(self): ...
    @property
    def displayname(self): ...
    @property
    def mangled_name(self): ...
    @property
    def location(self): ...
    @property
    def linkage(self): ...
    @property
    def tls_kind(self): ...
    @property
    def extent(self): ...
    @property
    def storage_class(self): ...
    @property
    def availability(self): ...
    @property
    def access_specifier(self): ...
    @property
    def type(self): ...
    @property
    def canonical(self): ...
    @property
    def result_type(self) -> Type: ...
    @property
    def exception_specification_kind(self): ...
    @property
    def underlying_typedef_type(self): ...
    @property
    def enum_type(self): ...
    @property
    def enum_value(self): ...
    @property
    def objc_type_encoding(self): ...
    @property
    def hash(self): ...
    @property
    def semantic_parent(self): ...
    @property
    def lexical_parent(self): ...
    @property
    def translation_unit(self): ...
    @property
    def referenced(self): ...
    @property
    def brief_comment(self): ...
    @property
    def raw_comment(self): ...
    def get_arguments(self) -> None: ...
    def get_num_template_arguments(self): ...
    def get_template_argument_kind(self, num): ...
    def get_template_argument_type(self, num): ...
    def get_template_argument_value(self, num): ...
    def get_template_argument_unsigned_value(self, num): ...
    def get_children(self): ...
    def walk_preorder(self) -> None: ...
    def get_tokens(self): ...
    def get_field_offsetof(self): ...
    def is_anonymous(self): ...
    def is_bitfield(self): ...
    def get_bitfield_width(self): ...
    @staticmethod
    def from_result(res, fn, args): ...
    @staticmethod
    def from_cursor_result(res, fn, args): ...

class StorageClass:
    value: Any
    def __init__(self, value) -> None: ...
    def from_param(self): ...
    @property
    def name(self): ...
    @staticmethod
    def from_id(id): ...

class AvailabilityKind(BaseEnumeration): ...

class AccessSpecifier(BaseEnumeration):

    def from_param(self): ...
    NONE = ...
    INVALID = ...
    PRIVATE = ...
    PROTECTED = ...
    PUBLIC = ...

class TypeKind(BaseEnumeration):
    @property
    def spelling(self): ...

class RefQualifierKind(BaseEnumeration):
    def from_param(self): ...

class LinkageKind(BaseEnumeration):
    def from_param(self): ...

class TLSKind(BaseEnumeration):
    def from_param(self): ...

class Type(Structure):
    @property
    def kind(self): ...
    parent: Any
    length: Any
    def argument_types(self): ...
    @property
    def element_type(self): ...
    @property
    def element_count(self): ...
    @property
    def translation_unit(self): ...
    @staticmethod
    def from_result(res, fn, args): ...
    def get_num_template_arguments(self): ...
    def get_template_argument_type(self, num): ...
    def get_canonical(self): ...
    def is_const_qualified(self): ...
    def is_volatile_qualified(self): ...
    def is_restrict_qualified(self): ...
    def is_function_variadic(self): ...
    def get_address_space(self): ...
    def get_typedef_name(self): ...
    def is_pod(self): ...
    def get_pointee(self): ...
    def get_declaration(self) -> Cursor: ...
    def get_result(self): ...
    def get_array_element_type(self): ...
    def get_array_size(self): ...
    def get_class_type(self): ...
    def get_named_type(self): ...
    def get_align(self): ...
    def get_size(self): ...
    def get_offset(self, fieldname): ...
    def get_ref_qualifier(self): ...
    def get_fields(self): ...
    def get_exception_specification_kind(self): ...
    @property
    def spelling(self): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...

class ClangObject:
    obj: Any
    def __init__(self, obj) -> None: ...
    def from_param(self): ...

class _CXUnsavedFile(Structure): ...

class CompletionChunk:
    class Kind:
        name: Any
        def __init__(self, name) -> None: ...
    cs: Any
    key: Any
    def __init__(self, completionString, key) -> None: ...
    def spelling(self): ...
    def kind(self): ...
    def string(self): ...
    def isKindOptional(self): ...
    def isKindTypedText(self): ...
    def isKindPlaceHolder(self): ...
    def isKindInformative(self): ...
    def isKindResultType(self): ...

class CompletionString(ClangObject):
    class Availability:
        name: Any
        def __init__(self, name) -> None: ...
    def __len__(self): ...
    def num_chunks(self): ...
    def __getitem__(self, key): ...
    @property
    def priority(self): ...
    @property
    def availability(self): ...
    @property
    def briefComment(self): ...

class CodeCompletionResult(Structure):
    @property
    def kind(self): ...
    @property
    def string(self): ...

class CCRStructure(Structure):
    def __len__(self): ...
    def __getitem__(self, key): ...

class CodeCompletionResults(ClangObject):
    ptr: Any
    def __init__(self, ptr) -> None: ...
    def from_param(self): ...
    def __del__(self) -> None: ...
    @property
    def results(self): ...
    ccr: Any
    @property
    def diagnostics(self): ...

class Index(ClangObject):
    @staticmethod
    def create(excludeDecls: bool = ...): ...
    def __del__(self) -> None: ...
    def read(self, path): ...
    def parse(self, path, args: Any | None = ..., unsaved_files: Any | None = ..., options: int = ...): ...

class TranslationUnit(ClangObject):
    PARSE_NONE: int
    PARSE_DETAILED_PROCESSING_RECORD: int
    PARSE_INCOMPLETE: int
    PARSE_PRECOMPILED_PREAMBLE: int
    PARSE_CACHE_COMPLETION_RESULTS: int
    PARSE_SKIP_FUNCTION_BODIES: int
    PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION: int
    @classmethod
    def from_source(cls, filename, args: Any | None = ..., unsaved_files: Any | None = ..., options: int = ..., index: Any | None = ...): ...
    @classmethod
    def from_ast_file(cls, filename, index: Any | None = ...): ...
    index: Any
    def __init__(self, ptr, index) -> None: ...
    def __del__(self) -> None: ...
    @property
    def cursor(self): ...
    @property
    def spelling(self): ...
    def get_includes(self): ...
    def get_file(self, filename): ...
    def get_location(self, filename, position): ...
    def get_extent(self, filename, locations): ...
    tu: Any
    @property
    def diagnostics(self): ...
    def reparse(self, unsaved_files: Any | None = ..., options: int = ...) -> None: ...
    def save(self, filename) -> None: ...
    def codeComplete(self, path, line, column, unsaved_files: Any | None = ..., include_macros: bool = ..., include_code_patterns: bool = ..., include_brief_comments: bool = ...): ...
    def get_tokens(self, locations: Any | None = ..., extent: Any | None = ...): ...

class File(ClangObject):
    @staticmethod
    def from_name(translation_unit, file_name): ...
    @property
    def name(self): ...
    @property
    def time(self): ...
    @staticmethod
    def from_result(res, fn, args): ...

class FileInclusion:
    source: Any
    include: Any
    location: Any
    depth: Any
    def __init__(self, src, tgt, loc, depth) -> None: ...
    @property
    def is_input_file(self): ...

class CompilationDatabaseError(Exception):
    ERROR_UNKNOWN: int
    ERROR_CANNOTLOADDATABASE: int
    cdb_error: Any
    def __init__(self, enumeration, message) -> None: ...

class CompileCommand:
    cmd: Any
    ccmds: Any
    def __init__(self, cmd, ccmds) -> None: ...
    @property
    def directory(self): ...
    @property
    def filename(self): ...
    @property
    def arguments(self) -> None: ...

class CompileCommands:
    ccmds: Any
    def __init__(self, ccmds) -> None: ...
    def __del__(self) -> None: ...
    def __len__(self): ...
    def __getitem__(self, i): ...
    @staticmethod
    def from_result(res, fn, args): ...

class CompilationDatabase(ClangObject):
    def __del__(self) -> None: ...
    @staticmethod
    def from_result(res, fn, args): ...
    @staticmethod
    def fromDirectory(buildDir): ...
    def getCompileCommands(self, filename): ...
    def getAllCompileCommands(self): ...

class Token(Structure):
    @property
    def spelling(self): ...
    @property
    def kind(self): ...
    @property
    def location(self): ...
    @property
    def extent(self): ...
    @property
    def cursor(self): ...

class LibclangError(Exception):
    m: Any
    def __init__(self, message) -> None: ...

class Config:
    library_path: Any
    library_file: Any
    compatibility_check: bool
    loaded: bool
    @staticmethod
    def set_library_path(path) -> None: ...
    @staticmethod
    def set_library_file(filename) -> None: ...
    @staticmethod
    def set_compatibility_check(check_status) -> None: ...
    def lib(self): ...
    def get_filename(self): ...
    def get_cindex_library(self): ...
    def function_exists(self, name): ...
