from __future__ import annotations
from logging import log
import logging
import os
from logzero import logger
from camel_snake_kebab import camelCase, snake_case
from .conf import Config
from .dom import (
    FACTORY,
    Context,
    NodeProxy,
    Bindable,
    EnumConstant,
    Method,
    Function,
    Record,
    Field,
    Enum,
    Namespace,
)
from orderedset import OrderedSet
import json

import graphlib


def c_decode(in_str: str) -> str:
    return json.loads(in_str.join('""' if '"' not in in_str else "''"))


def c_encode(in_str: str) -> str:
    """Encode a string literal as per C"""
    return json.dumps(in_str)[1:-1]


def emit(code, fragment):
    code.append(fragment)


anon_count = 0


def generate_enum(context: Context, enum: Enum, bindings, code):
    name = enum.name
    if enum.parent:
        qname = enum.fullname
        if isinstance(enum.parent, Namespace):
            parent = "m"
        else:
            parent = f"_{enum.parent.name}"
    else:
        qname = enum.name
        parent = "m"

    if not name:
        # anonymous enum
        # if isinstance(enum.parent, Record):
        #     emit(code, f"""\n\t// anonymous enum\n""")
        #     emit(code, f"""\t// {enum.location}\n""")
        #     for ec in enum._filter(EnumConstant):
        #         emit(code,
        #         f"""\t{parent}.attr("{ec.name}") = py::cast(int({enum.parent.fullname}::{ec.name}));\n""")
        #     emit(code, "\n")
        return

    if context.is_banned(enum):
        emit(code, f"\t// [banned] {enum.fullname}\n")
        emit(code, f"""\t// {enum.location}\n""")
        return
    if not enum.is_public():
        return
    emit(code, f"""\t// enum {name}\n""")
    emit(code, f"""\t// {enum.location}\n""")
    emit(code, f"""\tpy::enum_<{qname}>({parent}, "{name}", py::arithmetic())""")
    for ec in enum._filter(EnumConstant):
        emit(code, f"""\n\t\t.value("{ec.name}", {ec.fullname})""")
    if context.export_enum_values(enum):
        emit(code, f"""\n\t\t.export_values()""")
    emit(code, ";\n\n")


def is_getter(method: Method):
    name = method.name
    if camelCase(name) == name:
        name = snake_case(name)
    logger.warning("CHECK-GETTER %s %s, %s", method, name, method.parameters)
    if name.startswith('get_') and len(method.parameters) == 0:
        logger.warning("CHECK: %s BINGO", method)
        return True
    return False

def getter_prop_name(method):
    if is_getter(method):
        name = method.name
        if camelCase(name) == name:
            name = snake_case(name)
        return name[len('get_'):]


def is_setter(method: Method):
    name = method.name
    if camelCase(name) == name:
        name = snake_case(name)
    logger.warning("CHECK-SETTER %s %s", method, name)
    if name.startswith('set_') and len(method.parameters) == 1:
        return True
    return False

def setter_prop_name(method):
    if is_setter(method):
        name = method.name
        if camelCase(name) == name:
            name = snake_case(name)
        return name[len('set_'):]


def generate_record(context: Context, rec: Record, bindings, code):
    if context.is_banned(rec):
        emit(code, f"\t// [banned] {rec.fullname}\n\n")
        return
    if rec.is_private():
        emit(code, f"\t// [private] {rec.fullname}\n\n")
        return
    if not rec.name:
        return
    mro = rec.fullname
    mro = OrderedSet()
    mro.add(rec.fullname)
    for base in rec.bases:
        if base in bindings and not base.is_abstract():
            mro.add(base.fullname)
        else:
            logger.warning("base class not in bindings or abstract: %s %s", rec, base)
    mro = ', '.join(mro)
    handler_policy = context.get_handler_policy(rec)
    if handler_policy:
        mro += f", {handler_policy}<{rec.fullname}>"

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
                if (
                    dep not in bindings
                    and dep not in context.casters()
                    and not dep.is_builtin()
                ):
                    skip = f"// [{dep}] "
                    break

            emit(
                code,
                f"""\n\t{skip}_{rec.name}.def_readwrite("{fld.name}", &{rec.fullname}::{fld.name});""",
            )

    if context.config._emit_methods:

        overloads = {}
        for m in rec.methods:
            overloads.setdefault(m.name, []).append(m)

        # properties
        props = {}
        for method_name in list(overloads):
            methods = overloads.get(method_name)
            if not methods:
                continue
            if len(methods) != 1:
                continue
            method = methods[0]
            if context.is_banned(method):
                continue
            if is_getter(method):
                prop_name = getter_prop_name(method)

                props.setdefault(prop_name, {})['getter'] = method
                del overloads[method_name]
                if prop_name in overloads:
                    del overloads[prop_name]

            elif is_setter(method):

                if context.is_banned(method):
                    continue
                prop_name = setter_prop_name(method)

                props.setdefault(prop_name, {})['setter'] = method
                del overloads[method_name]
                # if prop_name in overloads:
                #     del overloads[prop_name]

        for name in props:
            prop_info = props[name]
            getter: Method | None = prop_info.get('getter')
            setter = prop_info.get('setter')
            if getter and setter:
                rbg= context.return_policy(getter)
                rbs= context.return_policy(setter)
                emit(code,
                f"""\n\t_{rec.name}.def_property("{name}", &{getter.fullname}, &{setter.fullname}""")
                if rbg:
                    emit(code, f", {rbg}")
                if rbs:
                    emit(code, f", {rbs}")
                emit(code, """);""")
            elif getter:
                rbg = context.return_policy(getter)
                defun = 'def_property_readonly'
                if getter.is_static():
                    defun = 'def_property_readonly_static'
                    gcode = f"[](py::object) {{ return {getter.fullname}(); }}"
                    if mcode := context.bind_with_lambda(getter):
                        logger.info("BINGO! %s %s", getter, mcode)
                        gcode = mcode
                    emit(code, f"""\n\t_{rec.name}.{defun}("{name}", {gcode}""")
                    if rbg:
                        emit(code, f", {rbg}")
                else:
                    gcode = context.bind_with_lambda(getter)
                    if gcode:
                        emit(code, f"""\n\t_{rec.name}.{defun}("{name}", {gcode}""")
                        if rbg:
                            emit(code, f", {rbg}")
                    else:
                        emit(code,
                        f"""\n\t_{rec.name}.{defun}("{name}", &{getter.fullname}""")
                        if rbg:
                            emit(code, f", {rbg}")
                emit(code, """);""")

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


def generate_method(
    context: Context, rec: Record, m: Method, overloaded: bool, bindings, code
):
    if not context.config._emit_methods:
        return
    skip = ""
    for dep in m.dependencies:
        if dep.name == "qreal":
            breakpoint()
        if (
            dep not in bindings
            and dep not in context.casters()
            and not dep.is_builtin()
        ):
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


def generate_function(
    context: Context, fun: Function, overloaded: bool, bindings: list, code
):
    skip = ""
    for dep in fun.dependencies:
        if (
            (dep not in bindings)
            and (dep not in context.casters())
            and not dep.is_builtin()
        ):
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
            funp = f"py::overload_cast<{fun.cpp_signature}>({funp})"
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
    for param in fun.parameters:
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


def generate(config: Config, outdir):
    # modname, bindings, config):
    ctx = Context(FACTORY, config)
    modname = config._module_name
    bindings = config._bindings
    config.dump()
    # seeding
    # generate initial includes
    header = []
    includes = []
    for name, paths in bindings.items():
        if isinstance(paths, str):
            includes.append(paths)
        elif isinstance(paths, list):
            includes += paths

    generate_includes(includes, header)

    generate_includes(
        config.cleaners + ["pybind11/pybind11.h"] + config.plugins, header
    )

    header = "".join(header)

    header_path = os.path.join(outdir, f"{modname}_module.hpp")

    with open(header_path, "w") as src:
        src.write(header)

    tx, inc = ctx.parse(header_path)
    tx.walk()
    records = []
    for name, path in bindings.items():
        if name == '*':
            records += list(tx._filter(Bindable))
            logger.warning("todo wildcard")
        else:
            try:
                binding = tx[name]
                if isinstance(binding, Namespace):
                    for b in binding._filter(Bindable):
                        records.append(b)
                elif isinstance(binding, Bindable):
                    records.append(binding)
                else:
                    logger.warning("non bindable: %s", binding)

            except KeyError:
                logger.warning("%s not found", name)

    casters = ctx.casters()
    for caster in casters:
        logger.info("caster for: %s", caster)

    def veto(bindable):
        if bindable in casters:
            logger.debug("veto caster: %s", bindable)
            return True
        if ctx.is_banned(bindable):
            logger.debug("banned: %s", bindable)
            return True
        return False

    deps: set[NodeProxy] = OrderedSet(records)
    star = OrderedSet()

    def seen(ship):
        return ship in deps or ship in star

    while deps:
        ship: NodeProxy = deps.pop()
        if veto(ship):
            continue
        logger.info("add %s", ship)
        star.add(ship)
        for dep in ship.dependencies:
            if veto(dep):
                continue
            if isinstance(dep, Bindable) and not seen(dep):
                logger.info("queue %s for %s", dep, ship.fullname)
                deps.add(dep)

        if isinstance(ship, Record):
            for members in (ship.fields, ship.methods, ship.constructors, ship.records, ship.enums):
                for member in members:
                    if veto(member):
                        continue
                    if member.is_public():
                        if isinstance(member, (Record, Enum)):
                            logger.info("queue member: %s:%s", ship.fullname, member.displayname)
                            deps.add(member)
                        else:
                            for dep in member.dependencies:
                                if veto(dep):
                                    continue
                                if isinstance(dep, Bindable) and not seen(dep):
                                    logger.info(
                                        "queue %s for member %s::%s",
                                        dep,
                                        ship.fullname,
                                        member.displayname,
                                    )
                                    deps.add(dep)

    topo = graphlib.TopologicalSorter()

    def filtered_deps(neutron):
        return [
            d for d in neutron.dependencies if isinstance(d, Bindable) and not veto(d)
        ]

    for neutron in star:
        topo.add(neutron, *filtered_deps(neutron))

    try:
        records = list(topo.static_order())
    except graphlib.CycleError as err:
        logger.error("could not sort: %s", err)
        breakpoint()
        print("what' up?")

    for rec in records:
        logger.info("binding %s", rec)

    code = []

    generate_module(ctx, modname, records, ctx.config._include_path, code)
    code = "".join(code)
    source_path = os.path.join(outdir, f"{modname}_module.cpp")

    with open(source_path, 'w') as src:
        src.write(code)
    return tx, inc, header, code


def main():
    import sys
    from .dom import logger
    logger.setLevel(logging.INFO)
    outdir = '.'
    if len(sys.argv) == 3:
        outdir = sys.argv[2]
    outdir = os.path.abspath(outdir)
    print("outdir:", outdir)
    if len(sys.argv) >= 2:
        config = Config.parse(sys.argv[1])
        generate(config, outdir)
    else:
        print("usage: python3 -m hydra.gen you_module_config.yaml [outdir]", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
