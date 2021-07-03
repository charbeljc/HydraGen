import graphlib
import logging
import os
from typing import get_args

from logzero import logger
from orderedset import OrderedSet

from . import conf, dom, gen
from .conf import Config
from .dom import Bindable, Namespace, NodeProxy, Record

dom.logger.setLevel(logging.INFO)

FLAGS = """-x c++ -fPIC -std=c++14 -fexceptions -DUSE_NAMESPACE=1
        -I/usr/include/c++/10/ -I/usr/include/x86_64-linux-gnu/c++/10/
        -I/usr/include/x86_64-linux-gnu/qt5/
        -I/usr/include/x86_64-linux-gnu/qt5/QtCore
        -I/usr/include/x86_64-linux-gnu/qt5/QtGui
        -I/usr/include/x86_64-linux-gnu/qt5/QtXml
        -I/home/rebelcat/Hack/hydrogen/src
        -I/home/rebelcat/Hack/hydrogen/build/src
        -I/home/rebelcat/Hack/hydra
        """

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
    ("H2Core::Timeline", "core/Timeline.h"),
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
    # ("H2Core::OssDriver", "core/IO/OssDriver.h"),
    ("H2Core::PortAudioDriver", "core/IO/PortAudioDriver.h"),
    ("H2Core::PortMidiDriver", "core/IO/PortMidiDriver.h"),
    ("H2Core::PulseAudioDriver", "core/IO/PulseAudioDriver.h"),
    # ("Song;IO/JackAudioDriver.h", ""),
    ("H2Core::TransportInfo", "core/IO/TransportInfo.h"),
    ("LashClient", "core/Lash/LashClient.h"),
    ("H2Core::LilyPond", "core/Lilipond/Lilypond.h"),
    ("H2Core::Sampler", "core/Sampler/Sampler.h"),
    ("H2Core::Synth", "core/Synth/Synth.h"),
]

CONFIG = (
    Config()
    .ban("QColor::QColor(QColor &&)")  # ban this constructor
    # .ban("QColor::name()")  # ban whole method, regardless of overloaded signatures
    .ban(
        "QColor::name(QColor::NameFormat)"
    )  # ban whole method, regardless of overloaded signatures
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
    # .ban("QObject::disconnect")
    .ban("QObject")
    .ban("QFileInfo::QFileInfo(QFileInfoPrivate *)")
    .ban("QFileInfo::operator=(QFileInfo &&)")
    .ban("QFileInfo::exists")
    .ban("H2Core::AlsaAudioDriver::AlsaAudioDriver()")
    .ban("H2Core::AlsaMidiDriver::midi_action")
    .ban("H2Core::JackAudioDriver::m_pClient")
    # std::vector
    .ban("H2Core::Synth::m_playingNotesQueue")
    .ban("H2Core::Hydrogen::m_nInstrumentLookupTable")
    .ban("H2Core::AlsaAudioDriver::m_pPlayback_handle")
    .ban("H2Core::PortAudioDriver::m_processCallback")
    .ban("H2Core::DiskWriterDriver::m_processCallback")
    .ban("H2Core::AlsaAudioDriver::m_processCallback")
    # Qt Reduction, phase 2
    .ban("H2Core::LadspaFX::m_pLibrary")
    .ban("H2Core::AudioEngine::m_EngineMutex")
    .ban("H2Core::AudioEngine::m_MutexOutputPointer")
    .ban("H2Core::AudioEngine::m_LockingThread")
    .ban("H2Core::AudioEngine::m_currentTickTime")
    .ban("QRgba64::operator=")
    .ban("QMetaType")
    .ban("QStringRef")
    .ban("QStringView")
    .ban("QByteArray")
    .ban("QChar")
    .ban("QDomNode")
    .ban("QFileInfo")
    .ban("QLatin1String")
    .ban("*::metaObject()")
    .ban("*::metaObject()")
    .ban("*::qt_metacall(QMetaObject::Call, int, void **)")
    .ban("*::qt_static_metacall(QObject *, QMetaObject::Call, int, void **)")
    # cflags and include paths
    .add_cflags(FLAGS)
    .add_include_path("/usr/include/python3.9")
    .add_include_path("/home/rebelcat/Hack/hydra/include")
    .add_include_path("/usr/include")
    # cleaners and plugins
    .add_cleaner("qtreset.h")
    .add_plugin("pybind11/stl.h")
    .add_plugin("pybind11/numpy.h")
    .add_plugin("qtcasters.h")
    .bind_with_lambda(
        "QColor",
        "name()",
        """[](const QColor &color) {
        return color.name();
    }""",
    )
    .bind_with_lambda(
        "H2Core::Sample",
        "get_data_l()",
        """[](const H2Core::Sample & sample) {
            size_t nframes = sample.get_frames();
            auto result = py::array_t<float>(nframes);
            py::buffer_info buf = result.request();
            float *ptr = static_cast<float *>(buf.ptr);
            float *src = sample.get_data_l();
            for (size_t idx = 0; idx < nframes; idx++) {
                ptr[idx] = src[idx];
            }
            return result;
        }
        """,
    )
    .bind_with_lambda(
        "H2Core::Sample",
        "get_data_r()",
        """[](const H2Core::Sample & sample) {
            size_t nframes = sample.get_frames();
            auto result = py::array_t<float>(nframes);
            py::buffer_info buf = result.request();
            float *ptr = static_cast<float *>(buf.ptr);
            float *src = sample.get_data_r();
            for (size_t idx = 0; idx < nframes; idx++) {
                ptr[idx] = src[idx];
            }
            return result;
        }
        """,
    )
    .add_method(
        "QColor",
        "__repr__",
        """[](const QColor &color) {
        return "QColor(\\"" + color.name() + "\\")";
    }""",
    )
    .add_method(
        "H2Core::Song",
        "__repr__",
        """[](const H2Core::Song & song) {
        return "<Song \\"" + song.getName() + "\\">";
    }
    """,
    )
    .add_method(
        "H2Core::Drumkit",
        "__repr__",
        """[](const H2Core::Drumkit & drumkit) {
        return "<Drumkit \\"" + drumkit.get_name() + "\\">";
    }
    """,
    )
    .add_method(
        "H2Core::DrumkitComponent",
        "__repr__",
        """[](const H2Core::DrumkitComponent & dkc) {
        return "<DrumkitComponent \\"" + dkc.get_name() + "\\">";
    }
    """,
    )
    .add_method(
        "H2Core::Instrument",
        "__repr__",
        """[](const H2Core::Instrument & instrument) {
        return "<Instrument \\"" + instrument.get_name() + "\\">";
    }
    """,
    )
    .add_method(
        "H2Core::Sample",
        "__repr__",
        """[](const H2Core::Sample & sample) {
        return "<Sample \\"" + sample.get_filename() + "\\">";
    }
    """,
    )
    .add_policy(
        "H2Core::Drumkit::get_instruments",
        "py::return_value_policy::reference_internal",
    )
    .add_policy("H2Core::Hydrogen::get_instance", "py::return_value_policy::reference")

    .add_prolog(
        """
        using namespace H2Core;\n\n
        """
    )
)


def main(config: Config, modname: str, bindings):
    # modname, bindings, config):
    ctx = dom.Context(dom.FACTORY, config)

    # seeding
    config.dump()
    # generate initial includes
    header = []
    includes = []
    for name, paths in bindings:
        if isinstance(paths, str):
            includes.append(paths)
        elif isinstance(paths, list):
            includes += paths

    gen.generate_includes(includes, header)

    gen.generate_includes(
        config.cleaners + ["pybind11/pybind11.h"] + config.plugins, header
    )

    header = "".join(header)

    with open(f"{modname}_module.hpp", "w") as src:
        src.write(header)

    tx, inc = ctx.parse(f"{modname}_module.hpp")
    tx.walk()
    records = []
    for name, path in bindings:
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
            logger.warning("banned: %s", bindable)
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
            for members in (ship.fields, ship.methods, ship.constructors):
                for member in members:
                    if veto(member):
                        continue
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

    gen.generate_module(
        ctx, modname, records, ["/home/rebelcat/Hack/hydrogen/src/"], code
    )
    code = "".join(code)

    with open(f"{modname}_module.cpp", "w") as src:
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
    main(CONFIG, "h2core", BINDINGS)
