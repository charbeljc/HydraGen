from __future__ import annotations
import textwrap
from typing import OrderedDict
from logzero import logger
from dom import NodeProxy, Record
from orderedset import OrderedSet

def emit(code, fragment):
    code.append(fragment)

def generate_record(rec: Record, code):
    emit(code, f"""   py::class_<{rec.name}>(m, "{rec.name}")"""
    )
    for ctor in rec.constructors:
        if not ctor.is_public():
            continue
        emit(code, f"""\n    .def(py::init<{ctor.cpp_signature}>())"""
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
            emit(code,
                f"""\n    .def("{m.name}", &{rec.name}::{m.name})"""
            )
        else:
            for m in signatures:
                if not m.is_public():
                    continue
                emit(code,
                    f"""\n    .def("{m.name}", py::overload_cast<{m.cpp_signature}>(&{rec.name}::{m.name}))"""
                )
    
    emit(code, """;\n\n"""
    )

def generate_module(name, records, include_paths, code):

    generate_imports(records, code, include_paths)
    
    emit(code, "#include <pybind11_bindings/qtreset.h>\n")
    emit(code, "#include <pybind11/pybind11.h>\n")
    emit(code, "namespace py = pybind11;\n\n")
    emit(code, "using namespace H2Core;\n\n")
    emit(code, f"PYBIND11_MODULE({name}, m) {{\n\n")
    for rec in records:
        generate_record(rec, code)

    emit(code, """}""")

def generate_imports(records, code, include_paths):
    files = OrderedSet()
    for record in records:
        files.add(record.location.file.name)

    for filename in files:
        for path in include_paths:
            if filename.startswith(path):
                emit(code, f"""#include <{filename[len(path):]}>\n"""
                )
    
