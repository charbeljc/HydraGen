from importlib import reload
import logging
from typing import get_args
from logzero import logger
from orderedset import OrderedSet
from . import conf, dom, gen
import os
import graphlib

reload(conf)
reload(dom)
reload(gen)

from .dom import Record, Bindable

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
    ("H2Core::Playlist", "core/Basics/Playlist.h"),
    ("H2Core::Pattern", "core/Basics/Pattern.h"),
    ("H2Core::PatternList", "core/Basics/PatternList.h"),
    ("H2Core::AutomationPath", "core/Basics/AutomationPath.h"),
    ("H2Core::Song", "core/Basics/Song.h"),
    ("H2Core::Hydrogen", "core/Hydrogen.h"),
    ("H2Core::AudioEngine", "core/AudioEngine.h"),
    # ("H2Core::CoreActionControler", "core/CoreActionControler.h"),
    ("H2Core::EventQueue", "core/EventQueue.h"),
    ("H2Core::H2Exception", "core/H2Exception.h"),
    ("Action", "core/MidiAction.h"),
    ("MidiActionManager::targeted_element", "core/MidiAction.h"),
    ("MidiActionManager", "core/MidiAction.h"),
    # (":MidiMap", "core/MidiMap.h"),
    # ("OscServer", "core/OscServer.h"),
    # ("H2Core::Timeline", "core/Timeline.h"),
    ("H2Core::get_version", "core/Version.h"),
    ("H2Core::version_older_than", "core/Version.h"),
    ("H2Core::Effects", "core/FX/Effects.h"),
    ("H2Core::LadspaFX", "core/FX/LadspaFX.h"),

    ("H2Core::AlsaAudioDriver", "core/IO/AlsaAudioDriver.h"),
    ("H2Core::AlsaMidiDriver", "core/IO/AlsaMidiDriver.h"),
    ("H2Core::AudioOutput", "core/IO/AudioOutput.h"),
    ("H2Core::CoreAudioDriver", "core/IO/CoreAudioDriver.h"),
    ("H2Core::CoreMidiDriver", "core/IO/CoreMidiDriver.h"),
    ("H2Core::DiskWriterDriver", "core/IO/DiskWriterDriver.h"),
    ("H2Core::FakeDriver", "core/IO/FakeDriver.h"),
    ("H2Core::JackAudioDriver", "core/IO/JackAudioDriver.h"),
    ("H2Core::JackMidiDriver", "core/IO/JackMidiDriver.h"),
    ("H2Core::MidiInput", "core/IO/MidiInput.h"),
    ("H2Core::MidiMessage", "core/IO/MidiCommon.h"),
    ("H2Core::MidiOutput", "core/IO/MidiOutput.h"),
    ("H2Core::MidiPortInfo", "core/IO/MidiCommon.h"),
    ("H2Core::NullDriver", "core/IO/NullDriver.h"),
    #("H2Core::OssDriver", "core/IO/OssDriver.h"),
    ("H2Core::PortAudioDriver", "core/IO/PortAudioDriver.h"),
    ("H2Core::PortMidiDriver", "core/IO/PortMidiDriver.h"),
    ("H2Core::PulseAudioDriver", "core/IO/PulseAudioDriver.h"),
    # ("Song;IO/JackAudioDriver.h", ""),
    ("H2Core::TransportInfo", "core/IO/TransportInfo.h"),
]


def fp(path):
    return os.path.join("/home/rebelcat/Hack/hydrogen/src/", path)


def main():
    config = (
        conf.Config()
        .ban("QColor::QColor(QColor &&)")  # ban this constructor
        .ban("QColor::name")  # ban whole method, regardless of signature
        .ban("QColor::operator=")
        .ban("H2Core::Note::match")
        .ban("H2Core::Pattern::find_note")
        .ban("std::thread::thread(const std::thread &)")
        .ban("std::thread::operator=(const std::thread &)")
        .ban("std::thread::operator=(std::thread &&)")
        .ban("std::thread::thread(std::thread &&)")
        .ban("std::timed_mutex::timed_mutex(const std::timed_mutex &)")
        .ban("std::timed_mutex::operator=")
        .ban("std::exception::operator=(std::exception &&)")
        .ban("std::exception::exception(std::exception &&)")
        .ban("std::__cow_string")
        .ban("std::__cow_string::operator=(std::__cow_string &&)")
        .ban("std::__cow_string::__cow_string(std::__cow_string &&)")
        .ban("std::runtime_error::operator=(std::runtime_error &&)")
        .ban("std::runtime_error::runtime_error(std::runtime_error &&)")
        .ban("targeted_element")
        .ban("MidiActionManager::targeted_element")
        .ban("_locker_struct")
        .ban("QDomNodePrivate")
        .ban("QStringList")
        .ban("QFileInfoPrivate")
        .ban("Entry")
        .ban("QObject::disconnect")
        .ban("QFileInfo::QFileInfo(QFileInfoPrivate *)")
        .ban("QFileInfo::operator=(QFileInfo &&)")
        .ban("QFileInfo::exists")
        .ban("H2Core::AlsaAudioDriver::AlsaAudioDriver()")
    )
    ctx = (
        dom.Context(dom.FACTORY, config)
        .set_flags(FLAGS)
        .add_flag("-I/usr/include/python3.9")
        .add_flag("-I/home/rebelcat/Hack/hydrogen/src/pybind11_bindings")
        .add_pybind11_plugin("pybind11/stl.h")
        .add_pybind11_plugin("custom_qt_casters.h")
    )

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
        try:
            class_def = tx[name]
            records.append(class_def)
        except KeyError:
            logger.warning("%s not found", name)

    casters = ctx.casters()

    def veto(bindable):
        if ctx.is_banned(bindable):
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

    try:
        records = list(topo.static_order())
    except graphlib.CycleError as err:
        logger.error("could not sort: %s", err)
        breakpoint()
        print("foo")

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

    gen.generate_module(
        ctx, "h2core", records, ["/home/rebelcat/Hack/hydrogen/src/"], code
    )
    code = "".join(code)

    with open("module.cpp", "w") as src:
        src.write(code)
    return tx, inc, header, code

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


if __name__ == "__main__":
    main()
