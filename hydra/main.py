from importlib import reload
import logging
from typing import get_args
from logzero import logger
from orderedset import OrderedSet
from . import dom, gen, walk
import os
import graphlib

reload(dom)
reload(gen)

from .dom import Record, Bindable, TypeRef

dom.logger.setLevel(logging.INFO)

FLAGS = """-x c++ -fPIC -std=c++14 -fexceptions -DUSE_NAMESPACE=1
        -I/usr/include/c++/10/ -I/usr/include/x86_64-linux-gnu/c++/10/
        -I/usr/include/x86_64-linux-gnu/qt5/
        -I/usr/include/x86_64-linux-gnu/qt5/QtCore
        -I/usr/include/x86_64-linux-gnu/qt5/QtGui
        -I/usr/include/x86_64-linux-gnu/qt5/QtXml
        -I/home/rebelcat/Hack/hydrogen/src
        -I/home/rebelcat/Hack/hydrogen/build/src
        -I/home/rebelcat/Hack/bindingtest
        """.split()

ctx = (
    dom.Context(dom.FACTORY, dom.Config())
    .set_flags(FLAGS)
    .add_flag("-I/usr/include/python3.9")
    .add_flag("-I/home/rebelcat/Hack/hydrogen/src/pybind11_bindings")
    .add_pybind11_plugin("pybind11/stl.h")
    .add_pybind11_plugin("custom_qt_casters.h")
)


def fp(path):
    return os.path.join("/home/rebelcat/Hack/hydrogen/src/", path)


BINDINGS = [
    ("H2Core::XMLNode", "core/Helpers/Xml.h"),
    ("H2Core::Drumkit", "core/Basics/Drumkit.h"),
    ("H2Core::DrumkitComponent", "core/Basics/DrumkitComponent.h"),
    ("H2Core::Instrument", "core/Basics/Instrument.h"),
    ("H2Core::InstrumentComponent", "core/Basics/InstrumentComponent.h"),
    ("H2Core::InstrumentLayer", "core/Basics/InstrumentLayer.h"),
    ("H2Core::InstrumentList", "core/Basics/InstrumentList.h"),
    ("H2Core::Sample", "core/Basics/Sample.h"),
    ("H2Core::Preferences", "core/Preferences.h"),
    ("H2Core::Pattern", "core/Basics/Pattern.h"),
    ("H2Core::PatternList", "core/Basics/PatternList.h"),
    ("H2Core::AutomationPath", "core/Basics/AutomationPath.h"),
    ("H2Core::Song", "core/Basics/Song.h"),
    ("H2Core::Hydrogen", "core/Hydrogen.h"),
]
header = []
gen.generate_includes([item[1] for item in BINDINGS], header)

# gen.generate_includes([
#     "QtXml/private/qdom_p.h"
# ], header)

gen.generate_includes(["qtreset.h", "pybind11/pybind11.h"] + ctx.plugins, header)
header = "".join(header)

with open("module.hpp", "w") as src:
    src.write(header)

tx, inc = ctx.parse("module.hpp")
tx.walk()
records = []
for name, path in BINDINGS:
    class_def = tx[name]
    records.append(class_def)

casters = ctx.casters()


def veto(bindable):
    if bindable.name in ("QDomNodePrivate", "QStringList"):
        return True
    return False


qstring = tx["QString"]
logger.warning("QString: %s", qstring)
deps = OrderedSet(records)
star = OrderedSet()
assert qstring not in deps
assert qstring in casters

while deps:
    ship = deps.pop()
    if ship in casters:
        logger.warning("VETO-CAST: %s", ship)
        continue
    if veto(ship):
        logger.warning("VETO: %s", ship)
        continue
    star.add(ship)
    logger.info("ADD(0) %s", ship)
    for dep in ship.dependencies:
        if dep in casters:
            logger.warning("VETO-CAST(1): %s", dep)
            continue
        if veto(dep):
            logger.warning("VETO: %s", dep)
            continue
        if dep not in deps and dep not in star and isinstance(dep, Bindable):
            logger.info("ADD(1) %s", dep)
            deps.add(dep)

    if isinstance(ship, Bindable) and isinstance(ship, Record):
        for members in (ship.fields, ship.methods, ship.constructors):
            for member in members:
                for dep in member.dependencies:
                    if dep in casters:
                        logger.warning("VETO-CAST: %s", dep)
                        continue
                    if veto(dep):
                        logger.warning("VETO(2): %s", dep)
                        continue
                    if dep not in star and isinstance(dep, Bindable):
                        logger.info("ADD(2) %s", dep)
                        star.add(dep)

topo = graphlib.TopologicalSorter()


def filtered_deps(neutron):
    return [
        d
        for d in neutron.dependencies
        if d not in casters and not veto(dep) and isinstance(dep, Bindable)
    ]


for neutron in star:
    topo.add(neutron, *filtered_deps(neutron))

records = list(topo.static_order())
assert qstring not in records

for rec in records:
    logger.info("binding %s", rec)
# while unseen:
#     dep = unseen.pop()

#     if isinstance(dep, TypeRef):
#         dep = dep.type
#     if not isinstance(dep, Bindable):
#         logger.warning("skip non bindable: %s", dep)
#         continue
#     deps.add(dep)
#     logger.info("new dep: %s", dep)
#     for d2 in dep.dependencies:
#         if d2 not in deps:
#             unseen.add(d2)
#             if isinstance(dep, Record):
#                 for m in dep.methods:
#                     for dd in m.dependencies:
#                         if dd not in deps:
#                             unseen.add(dd)

code = []

gen.generate_module(ctx, "h2core", records, ["/home/rebelcat/Hack/hydrogen/src/"], code)
code = "".join(code)

with open("module.cpp", "w") as src:
    src.write(code)

# import subprocess

# cmd = ["c++"] + ctx.flags + ["-c", "module.cpp"]

# process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
# process.wait()
# #out = process.stderr.read().decode()
# #print(out)

# cmd = ["c++", "-fPIC", "--shared", "-o", "h2core.so", "module.o",
# "/home/rebelcat/Hack/hydrogen/build/src/core/libhydrogen-core-1.1.0.so",
# "/lib/x86_64-linux-gnu/libQt5Xml.so.5"
# ]
# process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
# process.wait()
# out = process.stderr.read().decode()
# print(out)

# import h2core
