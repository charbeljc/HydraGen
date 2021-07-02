from __future__ import annotations
from functools import singledispatch
import textwrap
from typing import OrderedDict
from logzero import logger
from .dom import Context, EnumConstant, NodeProxy, Record, Enum, Namespace
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

    if '@' in qname:
        qname = "_anenum_%s" % anon_count
        anon_count += 1
        anon = True
        name = qname
    emit(code, f"""\tpy::enum_<{qname}>({parent}, "{name}")""")
    for ec in enum._filter(EnumConstant):
        if anon:
            emit(code, f"""\n\t\t.value("{ec.name}", {enum.parent.fullname}::{ec.name})""")
        else:
            emit(code, f"""\n\t\t.value("{ec.name}", {ec.fullname})""")
    if anon:
        emit(code, f"""\n\t\t.export_values()""")
    emit(code, ";\n\n")


def generate_record(context: Context, rec: Record, bindings, code):
    if context.is_banned(rec):
        emit(code, f"\t// [banned] {rec.fullname}\n\n")
        return
    emit(code, f"""\tpy::class_<{rec.fullname}> _{rec.name}(m, "{rec.name}");""")
    for ctor in rec.constructors:
        if not ctor.is_public():
            continue
        if context.is_banned(ctor):
            continue
        emit(code, f"""\n\t_{rec.name}.def(py::init<{ctor.cpp_signature}>());""")
    overloads = {}
    for m in rec.methods:
        overloads.setdefault(m.name, []).append(m)

    for name in overloads:
        signatures = overloads[name]
        if len(signatures) == 1:
            m = signatures[0]
            skip = ""
            for dep in m.dependencies:
                if dep not in bindings and dep not in context.casters():
                    skip = f"// [{dep}] "
                    break
            if not m.is_public():
                continue
            
            if context.is_banned(m):
                skip = "// [banned] "
            if m.node.is_static_method():
                emit(
                    code,
                    f"""\n\t{skip}_{rec.name}.def_static("{m.name}", &{rec.fullname}::{m.name}""",
                )
            else:
                emit(
                    code,
                    f"""\n\t{skip}_{rec.name}.def("{m.name}", &{rec.fullname}::{m.name}""",
                )
            if m.node.brief_comment:
                emit(
                    code,
                    f""",\n\t\t{skip}"{c_encode(m.node.brief_comment)}" """.strip(),
                )
            for param in m.parameters:
                emit(code, f""",\n\t{skip}\tpy::arg("{param.name}")""".strip())
            emit(code, ");")
        else:
            for m in signatures:
                skip = ""
                for dep in m.dependencies:
                    if dep not in bindings and dep not in context.casters():
                        skip = f"// [{dep}] "
                        break
                if not m.is_public():
                    continue
                if context.is_banned(m):
                    skip = "// [banned] "
                if m.node.is_static_method():
                    emit(
                        code,
                        f"""\n\t{skip}_{rec.name}.def_static("{m.name}_static", py::overload_cast<{m.cpp_signature}>(&{rec.fullname}::{m.name})""",
                    )
                else:
                    emit(
                        code,
                        f"""\n\t{skip}_{rec.name}.def("{m.name}", py::overload_cast<{m.cpp_signature}>(&{rec.fullname}::{m.name})""",
                    )
                if m.node.brief_comment:
                    emit(
                        code,
                        f""",\n\t\t{skip}\t"{c_encode(m.node.brief_comment)}" """.strip(),
                    )
                for param in m.parameters:
                    emit(code, f""",\n\t{skip}\tpy::arg("{param.name}")""".strip())
                emit(code, ");")

    emit(code, """\n\n""")


def generate_module(context: Context, name, bindings, include_paths, code):

    # generate_imports(records, code, include_paths)

    # emit(code, "#include <pybind11_bindings/qtreset.h>\n")
    # emit(code, "#include <pybind11/pybind11.h>\n")

    # generate_includes(context.plugins, code)
    generate_includes([f"{name}_module.hpp"], code)

    emit(code, "namespace py = pybind11;\n\n")
    emit(code, "using namespace H2Core;\n\n")
    emit(code, f"PYBIND11_MODULE({name}, m) {{\n\n")
    for binding in bindings:
        if isinstance(binding, Record):
            if binding.is_abstract():
                emit(code, f"// abstract class {binding.name}\n\n")
            else:
                generate_record(context, binding, bindings, code)
        elif isinstance(binding, Enum):
            generate_enum(context, binding, bindings, code)
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
