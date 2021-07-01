from __future__ import annotations
import textwrap
from typing import OrderedDict
from logzero import logger
from dom import NodeProxy, Record
from orderedset import OrderedSet
import json
def c_decode(in_str:str) -> str:
     return json.loads(in_str.join('""' if '"' not in in_str else "''"))

def c_encode(in_str:str) -> str:
     """ Encode a string literal as per C"""
     return json.dumps(in_str)[1:-1]



def emit(code, fragment):
    code.append(fragment)

def generate_record(rec: Record, code):
    emit(code, f"""\tpy::class_<{rec.fullname}>(m, "{rec.name}")"""
    )
    for ctor in rec.constructors:
        if not ctor.is_public():
            continue
        emit(code, f"""\n\t\t.def(py::init<{ctor.cpp_signature}>())"""
        )
    overloads = {}
    for m in rec.methods:
        overloads.setdefault(m.name, []).append(m)
    for name in overloads:
        signatures = overloads[name]
        if len(signatures) == 1:
            m = signatures[0]
            if not m.is_public():
                continue
            if m.node.is_static_method():
                emit(code,
                    f"""\n\t\t.def_static("{m.name}", &{rec.fullname}::{m.name}""")
            else:
                emit(code,
                    f"""\n\t\t.def("{m.name}", &{rec.fullname}::{m.name}""")
            if m.node.brief_comment:
                emit(code, f""",\n\t\t\t"{c_encode(m.node.brief_comment)}" """.strip()
            )
            for param in m.parameters:
                emit(code,
                f""",\n\t\t\tpy::arg("{param.name}")""".strip())
            emit(code,
                ")")
        else:
            for m in signatures:
                if not m.is_public():
                    continue
                if m.node.is_static_method():
                    emit(code,
                        f"""\n\t\t.def_static("{m.name}_static", py::overload_cast<{m.cpp_signature}>(&{rec.fullname}::{m.name})""")
                else:
                    emit(code,
                        f"""\n\t\t.def("{m.name}", py::overload_cast<{m.cpp_signature}>(&{rec.fullname}::{m.name})"""
                    )
                if m.node.brief_comment:
                    emit(code, f""",\n\t\t\t"{c_encode(m.node.brief_comment)}" """.strip()
                )
                for param in m.parameters:
                    emit(code,
                    f""",\n\t\t\tpy::arg("{param.name}")""".strip())
                emit(code,
                    ")")
    
    emit(code, """;\n\n"""
    )

def generate_module(context, name, records, include_paths, code):

    generate_imports(records, code, include_paths)
    
    emit(code, "#include <pybind11_bindings/qtreset.h>\n")
    emit(code, "#include <pybind11/pybind11.h>\n")

    generate_includes(context.plugins, code)

    emit(code, "namespace py = pybind11;\n\n")
    emit(code, "using namespace H2Core;\n\n")
    emit(code, f"PYBIND11_MODULE({name}, m) {{\n\n")
    for rec in records:
        generate_record(rec, code)

    emit(code, """}""")

def generate_imports(records, code, include_paths):
    files = OrderedSet()
    for record in records:
        name = record.location.file.name
        for path in include_paths:
            if name.startswith(path):
                files.add(record.location.file.name[len(path):])
                break

    generate_includes(files, code)

def generate_includes(files, code):
    for filename in files:
        emit(code, f"""#include <{filename}>\n""")
    
