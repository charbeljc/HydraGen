from __future__ import annotations
from functools import singledispatch
import textwrap
from typing import OrderedDict
from logzero import logger
from .dom import Context, EnumConstant, Method, Function, Record, Field, Enum, Namespace
from orderedset import OrderedSet
import json


def c_decode(in_str: str) -> str:
    return json.loads(in_str.join('""' if '"' not in in_str else "''"))


def c_encode(in_str: str) -> str:
    """Encode a string literal as per C"""
    return json.dumps(in_str)[1:-1]


def emit(code, fragment):
    code.append(fragment)


anon_count = 0


def generate_enum(context: Context, enum: Enum, bindings, code):
    global anon_count
    anon = False
    name = enum.name
    if context.is_banned(enum):
        emit(code, f"\t// [banned] {enum.fullname}\n\n")
        return
    if not enum.is_public():
        return
    emit(code, f"""\t// enum {name}\n""")
    if enum.parent:
        qname = enum.fullname
        if isinstance(enum.parent, Namespace):
            parent = "m"
        else:
            parent = f"_{enum.parent.name}"
    else:
        qname = enum.name
        parent = "m"

    if "@" in qname:
        qname = "_anenum_%s" % anon_count
        anon_count += 1
        anon = True
        name = qname
    emit(code, f"""\tpy::enum_<{qname}>({parent}, "{name}")""")
    for ec in enum._filter(EnumConstant):
        if anon:
            assert enum.parent
            emit(
                code,
                f"""\n\t\t.value("{ec.name}", {enum.parent.fullname}::{ec.name})""",
            )
        else:
            emit(code, f"""\n\t\t.value("{ec.name}", {ec.fullname})""")
    if anon:
        emit(code, f"""\n\t\t.export_values()""")
    emit(code, ";\n\n")


def generate_record(context: Context, rec: Record, bindings, code):
    if context.is_banned(rec):
        emit(code, f"\t// [banned] {rec.fullname}\n\n")
        return
    if rec.is_private():
        emit(code, f"\t// [private] {rec.fullname}\n\n")
        return
    mro = rec.fullname
    for base in rec.bases:
        if base in bindings and not base.is_abstract():
            mro +=  ', ' + base.fullname
        else:
            logger.warning("base class not in bindings or abstract: %s %s", rec, base)
    mro += f', std::shared_ptr<{rec.fullname}>'

    emit(code, f"""\tpy::class_<{mro}> _{rec.name}(m, "{rec.name}");""")

    if context.config._emit_ctors:

        for ctor in rec.constructors:
            if not ctor.is_public():
                continue
            if context.is_banned(ctor):
                continue
            emit(code, f"""\n\t_{rec.name}.def(py::init<{ctor.cpp_signature}>());""")

    if context.config._emit_fields:

        for fld in rec.fields:
            skip = ""
            if not fld.is_public():
                continue
            if context.is_banned(fld):
                continue
            for dep in fld.dependencies:
                if dep not in bindings and dep not in context.casters() and not dep.is_builtin():
                    skip = f"// [{dep}] "
                    break

            emit(code, f"""\n\t{skip}_{rec.name}.def_readwrite("{fld.name}", &{rec.fullname}::{fld.name});""")

    if context.config._emit_methods:

        overloads = {}
        for m in rec.methods:
            overloads.setdefault(m.name, []).append(m)

        for name in overloads:
            signatures = overloads[name]
            overloaded = len(signatures) > 1
            for m in signatures:
                generate_method(context, rec, m, overloaded, bindings, code)

    for name, mcode in context.get_addon_methods(rec):
        emit(
            code,
                f"""\n\t_{rec.name}.def("{name}",\n\t{mcode});""",
            )
    emit(code, """\n\n""")

def generate_method(context: Context, rec: Record, m: Method, overloaded: bool, bindings, code):
    if not context.config._emit_methods:
        return
    skip = ""
    for dep in m.dependencies:
        if dep.name == 'qreal':
            breakpoint()
        if dep not in bindings and dep not in context.casters() and not dep.is_builtin():
            skip = f"// [{dep}] "
            break
    if not m.is_public():
        return
    rb = context.return_policy(m)

    if context.is_banned(m):
        skip = "// [banned] "

    if mcode := context.bind_with_lambda(m):
        emit(
            code,
            f"""\n\t{skip}_{rec.name}.def("{m.name}",\n\t{mcode}""",
        )
    else:
        fun = f"&{rec.fullname}::{m.name}"
        name = m.name
        defun = "def"
        if overloaded:
            fun = f"py::overload_cast<{m.cpp_signature}>({fun})"
        if m.node.is_static_method():
            defun = "def_static"
            if overloaded:
                name = name + "_static"
        emit(
            code,
            f"""\n\t{skip}_{rec.name}.{defun}("{name}", {fun}""",
        )
    if m.node.brief_comment:
        emit(
            code,
            f""",\n\t\t{skip}"{c_encode(m.node.brief_comment)}" """.strip(),
        )
    for param in m.parameters:
        emit(code, f""",\n\t{skip}\tpy::arg("{param.name}")""".strip())
    if rb:
        emit(code, f",\n\t{rb}")
    emit(code, ");")
    
def generate_field(context: Context, fld: Field, bindings: list, code):
    breakpoint()

def generate_function(context: Context, fun: Function, overloaded: bool, bindings: list, code):
    skip = ""
    for dep in fun.dependencies:
        if (dep not in bindings) and (dep not in context.casters()) and not dep.is_builtin():
            skip = f"// [{dep}] "
            break
    if not fun.is_public():
        return

    if context.is_banned(fun):
        skip = "// [banned] "

    if mcode := context.bind_with_lambda(fun):
        emit(
            code,
            f"""\n\t{skip}m.def("{fun.name}",\n\t{mcode}""",
        )
    else:
        name = fun.name
        funp = f"&{fun.name}"
        defun = "def"
        if overloaded:
            funp = f"py::overload_cast<{m.cpp_signature}>({funp})"
        if fun.node.is_static_method():
            defun = "def_static"
            if overloaded:
                name = name + "_static"
        emit(
            code,
            f"""\n\t{skip}m.{defun}("{name}", {fun}""",
        )
    if fun.node.brief_comment:
        emit(
            code,
            f""",\n\t\t{skip}"{c_encode(fun.node.brief_comment)}" """.strip(),
        )
    for param in m.parameters:
        emit(code, f""",\n\t{skip}\tpy::arg("{param.name}")""".strip())
    emit(code, ");")


def generate_module(context: Context, name, bindings, include_paths, code):

    # generate_imports(records, code, include_paths)

    # emit(code, "#include <pybind11_bindings/qtreset.h>\n")
    # emit(code, "#include <pybind11/pybind11.h>\n")

    # generate_includes(context.plugins, code)
    generate_includes([f"{name}_module.hpp"], code)

    emit(code, "namespace py = pybind11;\n\n")

    for fragment in context.config._prolog:
        emit(code, fragment)
    emit(code, f"PYBIND11_MODULE({name}, m) {{\n\n")
    for binding in bindings:
        if isinstance(binding, Record):
            if binding.is_abstract():
                emit(code, f"// abstract class {binding.name}\n\n")
            else:
                generate_record(context, binding, bindings, code)
        elif isinstance(binding, Enum):
            generate_enum(context, binding, bindings, code)
        elif isinstance(binding, Function):
            generate_function(context, binding, False, bindings, code)
        else:
            logger.warning("don't know howto generate %s", binding)

    emit(code, """}""")


def generate_imports(records, code, include_paths):
    files = OrderedSet()
    for record in records:
        name = record.location.file.name
        for path in include_paths:
            if name.startswith(path):
                files.add(record.location.file.name[len(path) :])
                break

    generate_includes(files, code)


def generate_includes(files, code):
    for filename in files:
        emit(code, f"""#include <{filename}>\n""")
