#include <core/Basics/Sample.h>
#include <core/Object.h>
#include <core/Basics/InstrumentList.h>
#include <core/Basics/InstrumentLayer.h>
#include <core/Basics/InstrumentComponent.h>
#include <core/Basics/Instrument.h>
#include <core/Basics/DrumkitComponent.h>
#include <core/Basics/Drumkit.h>
#include <core/Helpers/Xml.h>
#include <pybind11_bindings/qtreset.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <custom_qt_casters.h>
namespace py = pybind11;

using namespace H2Core;

PYBIND11_MODULE(h2core, m) {

	py::class_<H2Core::Sample>(m, "Sample")
		.def(py::init<>())
		.def(py::init<const QString &, int, int, float *, float *>())
		.def(py::init<std::shared_ptr<Sample>>())
		.def_static("class_name", &H2Core::Sample::class_name)
		.def("write", &H2Core::Sample::write,
			"write sample to a file",
			py::arg("path"),
			py::arg("format"))
		.def_static("load_static", py::overload_cast<const QString &>(&H2Core::Sample::load),
			"Load a sample from a file.",
			py::arg("filepath"))
		.def_static("load_static", py::overload_cast<const QString &, const H2Core::Sample::Loops &, const H2Core::Sample::Rubberband &, const H2Core::Sample::VelocityEnvelope &, const H2Core::Sample::PanEnvelope &>(&H2Core::Sample::load),
			"Load a sample from a file and apply the transformations to the sample data.",
			py::arg("filepath"),
			py::arg("loops"),
			py::arg("rubber"),
			py::arg("velocity"),
			py::arg("pan"))
		.def("load", py::overload_cast<>(&H2Core::Sample::load),
			"Load the sample stored in #__filepath into #__data_l and #__data_r.")
		.def("unload", &H2Core::Sample::unload,
			"Flush the current content of the left and right channel and the current metadata.")
		.def("apply", &H2Core::Sample::apply,
			"Apply transformations to the sample data.",
			py::arg("loops"),
			py::arg("rubber"),
			py::arg("velocity"),
			py::arg("pan"))
		.def("apply_loops", &H2Core::Sample::apply_loops,
			"apply loop transformation to the sample",
			py::arg("lo"))
		.def("apply_velocity", &H2Core::Sample::apply_velocity,
			"apply velocity transformation to the sample",
			py::arg("v"))
		.def("apply_pan", &H2Core::Sample::apply_pan,
			"apply velocity transformation to the sample",
			py::arg("p"))
		.def("apply_rubberband", &H2Core::Sample::apply_rubberband,
			"apply rubberband transformation to the sample",
			py::arg("rb"))
		.def("exec_rubberband_cli", &H2Core::Sample::exec_rubberband_cli,
			"call rubberband cli to modify the sample",
			py::arg("rb"))
		.def("is_empty", &H2Core::Sample::is_empty,
			"Returns true if both data channels are null pointers")
		.def("get_filepath", &H2Core::Sample::get_filepath,
			"Returns #__filepath")
		.def("get_filename", &H2Core::Sample::get_filename,
			"Returns Filename part of #__filepath")
		.def("set_filepath", &H2Core::Sample::set_filepath,
			py::arg("filepath"))
		.def("set_filename", &H2Core::Sample::set_filename,
			py::arg("filename"))
		.def("set_frames", &H2Core::Sample::set_frames,
			"#__frames setter",
			py::arg("frames"))
		.def("get_frames", &H2Core::Sample::get_frames,
			"Returns #__frames accessor")
		.def("set_sample_rate", &H2Core::Sample::set_sample_rate,
			py::arg("sampleRate"))
		.def("get_sample_rate", &H2Core::Sample::get_sample_rate,
			"Returns #__sample_rate")
		.def("get_sample_duration", &H2Core::Sample::get_sample_duration,
			"Returns sample duration in seconds")
		.def("get_size", &H2Core::Sample::get_size,
			"Returns data size, which is calculated by #__frames time sizeof( float ) * 2")
		.def("get_data_l", &H2Core::Sample::get_data_l,
			"Returns #__data_l")
		.def("get_data_r", &H2Core::Sample::get_data_r,
			"Returns #__data_r")
		.def("set_is_modified", &H2Core::Sample::set_is_modified,
			"#__is_modified setter",
			py::arg("is_modified"))
		.def("get_is_modified", &H2Core::Sample::get_is_modified,
			"Returns #__is_modified")
		.def("get_pan_envelope", &H2Core::Sample::get_pan_envelope,
			"Returns #__pan_envelope")
		.def("get_velocity_envelope", &H2Core::Sample::get_velocity_envelope,
			"Returns #__velocity_envelope")
		.def("get_loops", &H2Core::Sample::get_loops,
			"Returns #__loops parameters")
		.def("get_rubberband", &H2Core::Sample::get_rubberband,
			"Returns #__rubberband parameters")
		.def_static("parse_loop_mode", &H2Core::Sample::parse_loop_mode,
			"parse the given string and rturn the corresponding loop_mode",
			py::arg("string"))
		.def("get_loop_mode_string", &H2Core::Sample::get_loop_mode_string,
			"Returns mode member of #__loops as a string")
		.def("toQString", &H2Core::Sample::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::EnvelopePoint>(m, "EnvelopePoint")
		.def(py::init<>())
		.def(py::init<const H2Core::EnvelopePoint &>())
		.def(py::init<int, int>());

	py::class_<H2Core::Sample::Rubberband>(m, "Rubberband")
		.def(py::init<>())
		.def(py::init<const H2Core::Sample::Rubberband *>())
		.def("operator==", &H2Core::Sample::Rubberband::operator==,
			"equal to operator",
			py::arg("b"))
		.def("toQString", &H2Core::Sample::Rubberband::toQString,
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::Sample::Loops>(m, "Loops")
		.def(py::init<>())
		.def(py::init<const H2Core::Sample::Loops *>())
		.def("operator==", &H2Core::Sample::Loops::operator==,
			"equal to operator",
			py::arg("b"))
		.def("toQString", &H2Core::Sample::Loops::toQString,
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::Object>(m, "Object")
		.def(py::init<>())
		.def(py::init<const H2Core::Object &>())
		.def(py::init<const char *>())
		.def("class_name", &H2Core::Object::class_name)
		.def_static("set_count", &H2Core::Object::set_count,
			"enable/disable class instances counting",
			py::arg("flag"))
		.def_static("count_active", &H2Core::Object::count_active)
		.def_static("objects_count", &H2Core::Object::objects_count)
		.def_static("write_objects_map_to", &H2Core::Object::write_objects_map_to,
			"output the full objects map to a given ostream",
			py::arg("out"),
			py::arg("map"))
		.def_static("write_objects_map_to_cerr", &H2Core::Object::write_objects_map_to_cerr)
		.def_static("bootstrap", &H2Core::Object::bootstrap,
			"must be called before any Object instantiation !",
			py::arg("logger"),
			py::arg("count"))
		.def_static("logger", &H2Core::Object::logger)
		.def_static("getAliveObjectCount", &H2Core::Object::getAliveObjectCount,
			"Returns Total numbers of objects being alive.")
		.def_static("getObjectMap", &H2Core::Object::getObjectMap,
			"Returns Copy of the object map.")
		.def_static("printObjectMapDiff", &H2Core::Object::printObjectMapDiff,
			"Creates the difference between a snapshot of the object map and its current state and prints it to std::cout.",
			py::arg("map"))
		.def("toQString", &H2Core::Object::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"))
		.def("Print", &H2Core::Object::Print,
			"Prints content of toQString() via DEBUGLOG",
			py::arg("bShort"));

	py::class_<H2Core::InstrumentList>(m, "InstrumentList")
		.def(py::init<>())
		.def(py::init<H2Core::InstrumentList *>())
		.def_static("class_name", &H2Core::InstrumentList::class_name)
		.def("size", &H2Core::InstrumentList::size,
			"returns the numbers of instruments")
		.def("operator<<", &H2Core::InstrumentList::operator<<,
			"add an instrument to the list",
			py::arg("instrument"))
		.def("operator[]", &H2Core::InstrumentList::operator[],
			"get an instrument from the list",
			py::arg("idx"))
		.def("add", &H2Core::InstrumentList::add,
			"add an instrument to the list",
			py::arg("instrument"))
		.def("insert", &H2Core::InstrumentList::insert,
			"insert an instrument into the list",
			py::arg("idx"),
			py::arg("instrument"))
		.def("is_valid_index", &H2Core::InstrumentList::is_valid_index,
			"check if there is a idx is a valid index for this list without throwing an error messaage",
			py::arg("idx"))
		.def("get", &H2Core::InstrumentList::get,
			"get an instrument from the list",
			py::arg("idx"))
		.def("del", py::overload_cast<int>(&H2Core::InstrumentList::del),
			"remove the instrument at a given index, does not delete it",
			py::arg("idx"))
		.def("del", py::overload_cast<std::shared_ptr<Instrument>>(&H2Core::InstrumentList::del),
			"remove an instrument from the list, does not delete it",
			py::arg("instrument"))
		.def("index", &H2Core::InstrumentList::index,
			"get the index of an instrument within the instruments",
			py::arg("instrument"))
		.def("find", py::overload_cast<const int>(&H2Core::InstrumentList::find),
			"find an instrument within the instruments",
			py::arg("i"))
		.def("find", py::overload_cast<const QString &>(&H2Core::InstrumentList::find),
			"find an instrument within the instruments",
			py::arg("name"))
		.def("findMidiNote", &H2Core::InstrumentList::findMidiNote,
			"find an instrument which play the given midi note",
			py::arg("note"))
		.def("swap", &H2Core::InstrumentList::swap,
			"swap the instruments of two different indexes",
			py::arg("idx_a"),
			py::arg("idx_b"))
		.def("move", &H2Core::InstrumentList::move,
			"move an instrument from a position to another",
			py::arg("idx_a"),
			py::arg("idx_b"))
		.def("load_samples", &H2Core::InstrumentList::load_samples,
			"Calls the Instrument::load_samples() member function of all Instruments in #__instruments.")
		.def("unload_samples", &H2Core::InstrumentList::unload_samples,
			"Calls the Instrument::unload_samples() member function of all Instruments in #__instruments.")
		.def("save_to", &H2Core::InstrumentList::save_to,
			"save the instrument list within the given XMLNode",
			py::arg("node"),
			py::arg("component_id"))
		.def_static("load_from", &H2Core::InstrumentList::load_from,
			"load an instrument list from an XMLNode",
			py::arg("node"),
			py::arg("dk_path"),
			py::arg("dk_name"))
		.def("fix_issue_307", &H2Core::InstrumentList::fix_issue_307,
			"Fix GitHub issue #307, so called \"Hi Bongo fiasco\".")
		.def("has_all_midi_notes_same", &H2Core::InstrumentList::has_all_midi_notes_same,
			"Check if all instruments have assigned the same MIDI out note")
		.def("set_default_midi_out_notes", &H2Core::InstrumentList::set_default_midi_out_notes,
			"Set each instrument consecuteve MIDI out notes, starting from 36")
		.def("toQString", &H2Core::InstrumentList::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::InstrumentLayer>(m, "InstrumentLayer")
		.def(py::init<std::shared_ptr<Sample>>())
		.def(py::init<std::shared_ptr<InstrumentLayer>>())
		.def(py::init<std::shared_ptr<InstrumentLayer>, std::shared_ptr<Sample>>())
		.def_static("class_name", &H2Core::InstrumentLayer::class_name)
		.def("set_gain", &H2Core::InstrumentLayer::set_gain,
			"set the gain of the layer",
			py::arg("gain"))
		.def("get_gain", &H2Core::InstrumentLayer::get_gain,
			"get the gain of the layer")
		.def("set_pitch", &H2Core::InstrumentLayer::set_pitch,
			"set the pitch of the layer",
			py::arg("pitch"))
		.def("get_pitch", &H2Core::InstrumentLayer::get_pitch,
			"get the pitch of the layer")
		.def("set_start_velocity", &H2Core::InstrumentLayer::set_start_velocity,
			"set the start ivelocity of the layer",
			py::arg("start"))
		.def("get_start_velocity", &H2Core::InstrumentLayer::get_start_velocity,
			"get the start velocity of the layer")
		.def("set_end_velocity", &H2Core::InstrumentLayer::set_end_velocity,
			"set the end velocity of the layer",
			py::arg("end"))
		.def("get_end_velocity", &H2Core::InstrumentLayer::get_end_velocity,
			"get the end velocity of the layer")
		.def("set_sample", &H2Core::InstrumentLayer::set_sample,
			"set the sample of the layer",
			py::arg("sample"))
		.def("get_sample", &H2Core::InstrumentLayer::get_sample,
			"get the sample of the layer")
		.def("load_sample", &H2Core::InstrumentLayer::load_sample,
			"Calls the #H2Core::Sample::load() member function of #__sample.")
		.def("unload_sample", &H2Core::InstrumentLayer::unload_sample)
		.def("save_to", &H2Core::InstrumentLayer::save_to,
			"save the instrument layer within the given XMLNode",
			py::arg("node"))
		.def_static("load_from", &H2Core::InstrumentLayer::load_from,
			"load an instrument layer from an XMLNode",
			py::arg("node"),
			py::arg("dk_path"))
		.def("toQString", &H2Core::InstrumentLayer::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::InstrumentComponent>(m, "InstrumentComponent")
		.def(py::init<int>())
		.def(py::init<std::shared_ptr<InstrumentComponent>>())
		.def_static("class_name", &H2Core::InstrumentComponent::class_name)
		.def("save_to", &H2Core::InstrumentComponent::save_to,
			py::arg("node"),
			py::arg("component_id"))
		.def_static("load_from", &H2Core::InstrumentComponent::load_from,
			py::arg("node"),
			py::arg("dk_path"))
		.def("operator[]", &H2Core::InstrumentComponent::operator[],
			py::arg("idx"))
		.def("get_layer", &H2Core::InstrumentComponent::get_layer,
			py::arg("idx"))
		.def("set_layer", &H2Core::InstrumentComponent::set_layer,
			py::arg("layer"),
			py::arg("idx"))
		.def("set_drumkit_componentID", &H2Core::InstrumentComponent::set_drumkit_componentID,
			"Sets the component ID #__related_drumkit_componentID",
			py::arg("related_drumkit_componentID"))
		.def("get_drumkit_componentID", &H2Core::InstrumentComponent::get_drumkit_componentID,
			"Returns the component ID of the drumkit.")
		.def("set_gain", &H2Core::InstrumentComponent::set_gain,
			py::arg("gain"))
		.def("get_gain", &H2Core::InstrumentComponent::get_gain)
		.def_static("getMaxLayers", &H2Core::InstrumentComponent::getMaxLayers,
			"Returns #m_nMaxLayers.")
		.def_static("setMaxLayers", &H2Core::InstrumentComponent::setMaxLayers,
			py::arg("layers"))
		.def("toQString", &H2Core::InstrumentComponent::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::Instrument>(m, "Instrument")
		.def(py::init<const int, const QString &, std::shared_ptr<ADSR>>())
		.def(py::init<std::shared_ptr<Instrument>>())
		.def_static("class_name", &H2Core::Instrument::class_name)
		.def_static("load_instrument", &H2Core::Instrument::load_instrument,
			"creates a new Instrument, loads samples from a given instrument within a given drumkit",
			py::arg("drumkit_name"),
			py::arg("instrument_name"),
			py::arg("lookup"))
		.def("load_from", py::overload_cast<const QString &, const QString &, bool, Filesystem::Lookup>(&H2Core::Instrument::load_from),
			"loads instrument from a given instrument within a given drumkit into a `live` Instrument object.",
			py::arg("drumkit_name"),
			py::arg("instrument_name"),
			py::arg("is_live"),
			py::arg("lookup"))
		.def("load_from", py::overload_cast<H2Core::Drumkit *, std::shared_ptr<Instrument>, bool>(&H2Core::Instrument::load_from),
			"loads instrument from a given instrument into a `live` Instrument object.",
			py::arg("drumkit"),
			py::arg("instrument"),
			py::arg("is_live"))
		.def_static("load_from_static", py::overload_cast<H2Core::XMLNode *, const QString &, const QString &>(&H2Core::Instrument::load_from),
			"load an instrument from an XMLNode",
			py::arg("node"),
			py::arg("dk_path"),
			py::arg("dk_name"))
		.def("load_samples", &H2Core::Instrument::load_samples,
			"Calls the InstrumentLayer::load_sample() member function of all layers of each component of the Instrument.")
		.def("unload_samples", &H2Core::Instrument::unload_samples,
			"Calls the InstrumentLayer::unload_sample() member function of all layers of each component of the Instrument.")
		.def("save_to", &H2Core::Instrument::save_to,
			"save the instrument within the given XMLNode",
			py::arg("node"),
			py::arg("component_id"))
		.def("set_name", &H2Core::Instrument::set_name,
			"Sets the name of the Instrument #__name.",
			py::arg("name"))
		.def("get_name", &H2Core::Instrument::get_name,
			"Access the name of the Instrument.")
		.def("set_id", &H2Core::Instrument::set_id,
			"Sets #__id to id.",
			py::arg("id"))
		.def("get_id", &H2Core::Instrument::get_id,
			"Returns #__id.")
		.def("set_adsr", &H2Core::Instrument::set_adsr,
			"set the ADSR of the instrument",
			py::arg("adsr"))
		.def("get_adsr", &H2Core::Instrument::get_adsr,
			"get the ADSR of the instrument")
		.def("copy_adsr", &H2Core::Instrument::copy_adsr,
			"get a copy of the ADSR of the instrument")
		.def("set_mute_group", &H2Core::Instrument::set_mute_group,
			"set the mute group of the instrument",
			py::arg("group"))
		.def("get_mute_group", &H2Core::Instrument::get_mute_group,
			"get the mute group of the instrument")
		.def("set_midi_out_channel", &H2Core::Instrument::set_midi_out_channel,
			"set the midi out channel of the instrument",
			py::arg("channel"))
		.def("get_midi_out_channel", &H2Core::Instrument::get_midi_out_channel,
			"get the midi out channel of the instrument")
		.def("set_midi_out_note", &H2Core::Instrument::set_midi_out_note,
			"set the midi out note of the instrument",
			py::arg("note"))
		.def("get_midi_out_note", &H2Core::Instrument::get_midi_out_note,
			"get the midi out note of the instrument")
		.def("set_muted", &H2Core::Instrument::set_muted,
			"set muted status of the instrument",
			py::arg("muted"))
		.def("is_muted", &H2Core::Instrument::is_muted,
			"get muted status of the instrument")
		.def("setPan", &H2Core::Instrument::setPan,
			"set pan of the instrument",
			py::arg("val"))
		.def("setPanWithRangeFrom0To1", &H2Core::Instrument::setPanWithRangeFrom0To1,
			"set pan of the instrument, assuming the input range in [0;1]",
			py::arg("fVal"))
		.def("getPan", &H2Core::Instrument::getPan,
			"get pan of the instrument")
		.def("getPanWithRangeFrom0To1", &H2Core::Instrument::getPanWithRangeFrom0To1,
			"get pan of the instrument scaling and translating the range from [-1;1] to [0;1]")
		.def("set_gain", &H2Core::Instrument::set_gain,
			"set gain of the instrument",
			py::arg("gain"))
		.def("get_gain", &H2Core::Instrument::get_gain,
			"get gain of the instrument")
		.def("set_volume", &H2Core::Instrument::set_volume,
			"set the volume of the instrument",
			py::arg("volume"))
		.def("get_volume", &H2Core::Instrument::get_volume,
			"get the volume of the instrument")
		.def("set_filter_active", &H2Core::Instrument::set_filter_active,
			"activate the filter of the instrument",
			py::arg("active"))
		.def("is_filter_active", &H2Core::Instrument::is_filter_active,
			"get the status of the filter of the instrument")
		.def("set_filter_resonance", &H2Core::Instrument::set_filter_resonance,
			"set the filter resonance of the instrument",
			py::arg("val"))
		.def("get_filter_resonance", &H2Core::Instrument::get_filter_resonance,
			"get the filter resonance of the instrument")
		.def("set_filter_cutoff", &H2Core::Instrument::set_filter_cutoff,
			"set the filter cutoff of the instrument",
			py::arg("val"))
		.def("get_filter_cutoff", &H2Core::Instrument::get_filter_cutoff,
			"get the filter cutoff of the instrument")
		.def("set_peak_l", &H2Core::Instrument::set_peak_l,
			"set the left peak of the instrument",
			py::arg("val"))
		.def("get_peak_l", &H2Core::Instrument::get_peak_l,
			"get the left peak of the instrument")
		.def("set_peak_r", &H2Core::Instrument::set_peak_r,
			"set the right peak of the instrument",
			py::arg("val"))
		.def("get_peak_r", &H2Core::Instrument::get_peak_r,
			"get the right peak of the instrument")
		.def("set_fx_level", &H2Core::Instrument::set_fx_level,
			"set the fx level of the instrument",
			py::arg("level"),
			py::arg("index"))
		.def("get_fx_level", &H2Core::Instrument::get_fx_level,
			"get the fx level of the instrument",
			py::arg("index"))
		.def("set_random_pitch_factor", &H2Core::Instrument::set_random_pitch_factor,
			"set the random pitch factor of the instrument",
			py::arg("val"))
		.def("get_random_pitch_factor", &H2Core::Instrument::get_random_pitch_factor,
			"get the random pitch factor of the instrument")
		.def("set_pitch_offset", &H2Core::Instrument::set_pitch_offset,
			"set the pitch offset of the instrument",
			py::arg("val"))
		.def("get_pitch_offset", &H2Core::Instrument::get_pitch_offset,
			"get the pitch offset of the instrument")
		.def("set_active", &H2Core::Instrument::set_active,
			"set the active status of the instrument",
			py::arg("active"))
		.def("is_active", &H2Core::Instrument::is_active,
			"get the active status of the instrument")
		.def("set_soloed", &H2Core::Instrument::set_soloed,
			"set the soloed status of the instrument",
			py::arg("soloed"))
		.def("is_soloed", &H2Core::Instrument::is_soloed,
			"get the soloed status of the instrument")
		.def("enqueue", &H2Core::Instrument::enqueue,
			"enqueue the instrument")
		.def("dequeue", &H2Core::Instrument::dequeue,
			"dequeue the instrument")
		.def("is_queued", &H2Core::Instrument::is_queued,
			"get the queued status of the instrument")
		.def("set_stop_notes", &H2Core::Instrument::set_stop_notes,
			"set the stop notes status of the instrument",
			py::arg("stopnotes"))
		.def("is_stop_notes", &H2Core::Instrument::is_stop_notes,
			"get the stop notes of the instrument")
		.def("set_sample_selection_alg", &H2Core::Instrument::set_sample_selection_alg,
			py::arg("selected_algo"))
		.def("sample_selection_alg", &H2Core::Instrument::sample_selection_alg)
		.def("set_hihat_grp", &H2Core::Instrument::set_hihat_grp,
			py::arg("hihat_grp"))
		.def("get_hihat_grp", &H2Core::Instrument::get_hihat_grp)
		.def("set_lower_cc", &H2Core::Instrument::set_lower_cc,
			py::arg("message"))
		.def("get_lower_cc", &H2Core::Instrument::get_lower_cc)
		.def("set_higher_cc", &H2Core::Instrument::set_higher_cc,
			py::arg("message"))
		.def("get_higher_cc", &H2Core::Instrument::get_higher_cc)
		.def("set_drumkit_name", &H2Core::Instrument::set_drumkit_name,
			py::arg("name"))
		.def("get_drumkit_name", &H2Core::Instrument::get_drumkit_name)
		.def("set_is_preview_instrument", &H2Core::Instrument::set_is_preview_instrument,
			"Mark the instrument as hydrogen's preview instrument",
			py::arg("isPreview"))
		.def("is_preview_instrument", &H2Core::Instrument::is_preview_instrument)
		.def("set_is_metronome_instrument", &H2Core::Instrument::set_is_metronome_instrument,
			"Mark the instrument as metronome instrument",
			py::arg("isMetronome"))
		.def("is_metronome_instrument", &H2Core::Instrument::is_metronome_instrument)
		.def("get_components", &H2Core::Instrument::get_components)
		.def("get_component", &H2Core::Instrument::get_component,
			py::arg("DrumkitComponentID"))
		.def("set_apply_velocity", &H2Core::Instrument::set_apply_velocity,
			py::arg("apply_velocity"))
		.def("get_apply_velocity", &H2Core::Instrument::get_apply_velocity)
		.def("is_currently_exported", &H2Core::Instrument::is_currently_exported)
		.def("set_currently_exported", &H2Core::Instrument::set_currently_exported,
			py::arg("isCurrentlyExported"))
		.def("has_missing_samples", &H2Core::Instrument::has_missing_samples)
		.def("set_missing_samples", &H2Core::Instrument::set_missing_samples,
			py::arg("bHasMissingSamples"))
		.def("toQString", &H2Core::Instrument::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::DrumkitComponent>(m, "DrumkitComponent")
		.def(py::init<const int, const QString &>())
		.def(py::init<H2Core::DrumkitComponent *>())
		.def_static("class_name", &H2Core::DrumkitComponent::class_name)
		.def("save_to", &H2Core::DrumkitComponent::save_to,
			py::arg("node"))
		.def_static("load_from_static", py::overload_cast<H2Core::XMLNode *, const QString &>(&H2Core::DrumkitComponent::load_from),
			py::arg("node"),
			py::arg("dk_path"))
		.def("load_from", py::overload_cast<H2Core::DrumkitComponent *, bool>(&H2Core::DrumkitComponent::load_from),
			py::arg("component"),
			py::arg("is_live"))
		.def("set_name", &H2Core::DrumkitComponent::set_name,
			"Sets the name of the DrumkitComponent #__name.",
			py::arg("name"))
		.def("get_name", &H2Core::DrumkitComponent::get_name,
			"Access the name of the DrumkitComponent.")
		.def("set_id", &H2Core::DrumkitComponent::set_id,
			py::arg("id"))
		.def("get_id", &H2Core::DrumkitComponent::get_id)
		.def("set_volume", &H2Core::DrumkitComponent::set_volume,
			py::arg("volume"))
		.def("get_volume", &H2Core::DrumkitComponent::get_volume)
		.def("set_muted", &H2Core::DrumkitComponent::set_muted,
			py::arg("muted"))
		.def("is_muted", &H2Core::DrumkitComponent::is_muted)
		.def("set_soloed", &H2Core::DrumkitComponent::set_soloed,
			py::arg("soloed"))
		.def("is_soloed", &H2Core::DrumkitComponent::is_soloed)
		.def("set_peak_l", &H2Core::DrumkitComponent::set_peak_l,
			py::arg("val"))
		.def("get_peak_l", &H2Core::DrumkitComponent::get_peak_l)
		.def("set_peak_r", &H2Core::DrumkitComponent::set_peak_r,
			py::arg("val"))
		.def("get_peak_r", &H2Core::DrumkitComponent::get_peak_r)
		.def("reset_outs", &H2Core::DrumkitComponent::reset_outs,
			py::arg("nFrames"))
		.def("set_outs", &H2Core::DrumkitComponent::set_outs,
			py::arg("nBufferPos"),
			py::arg("valL"),
			py::arg("valR"))
		.def("get_out_L", &H2Core::DrumkitComponent::get_out_L,
			py::arg("nBufferPos"))
		.def("get_out_R", &H2Core::DrumkitComponent::get_out_R,
			py::arg("nBufferPos"))
		.def("toQString", &H2Core::DrumkitComponent::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::Drumkit>(m, "Drumkit")
		.def(py::init<>())
		.def(py::init<H2Core::Drumkit *>())
		.def_static("class_name", &H2Core::Drumkit::class_name)
		.def_static("load", &H2Core::Drumkit::load,
			"Load drumkit information from a directory.",
			py::arg("dk_dir"),
			py::arg("load_samples"))
		.def_static("load_by_name", &H2Core::Drumkit::load_by_name,
			"Simple wrapper for load() used with the drumkit's name instead of its directory.",
			py::arg("dk_name"),
			py::arg("load_samples"),
			py::arg("lookup"))
		.def_static("load_file", &H2Core::Drumkit::load_file,
			"Load a Drumkit from a file.",
			py::arg("dk_path"),
			py::arg("load_samples"))
		.def("load_samples", &H2Core::Drumkit::load_samples,
			"Calls the InstrumentList::load_samples() member function of #__instruments.")
		.def("unload_samples", &H2Core::Drumkit::unload_samples,
			"Calls the InstrumentList::unload_samples() member function of #__instruments.")
		.def_static("upgrade_drumkit", &H2Core::Drumkit::upgrade_drumkit,
			"Saves the current drumkit to dk_path, but makes a backup. This is used when the drumkit did not comply to our xml schema.",
			py::arg("pDrumkit"),
			py::arg("dk_path"))
		.def_static("user_drumkit_exists", &H2Core::Drumkit::user_drumkit_exists,
			"check if a user drumkit with the given name already exists",
			py::arg("dk_path"))
		.def("save", py::overload_cast<bool>(&H2Core::Drumkit::save),
			"save a drumkit, xml file and samples",
			py::arg("overwrite"))
		.def("save", py::overload_cast<const QString &, bool>(&H2Core::Drumkit::save),
			"save a drumkit, xml file and samples neither #__path nor #__name are updated",
			py::arg("dk_dir"),
			py::arg("overwrite"))
		.def_static("save_static", py::overload_cast<const QString &, const QString &, const QString &, const QString &, const QString &, const QString &, H2Core::InstrumentList *, std::vector<DrumkitComponent *> *, bool>(&H2Core::Drumkit::save),
			"save a drumkit using given parameters and an instrument list",
			py::arg("sName"),
			py::arg("sAuthor"),
			py::arg("sInfo"),
			py::arg("sLicense"),
			py::arg("sImage"),
			py::arg("sImageLicense"),
			py::arg("pInstruments"),
			py::arg("pComponents"),
			py::arg("bOverwrite"))
		.def("save_file", &H2Core::Drumkit::save_file,
			"save a drumkit into an xml file",
			py::arg("dk_path"),
			py::arg("overwrite"),
			py::arg("component_id"))
		.def("save_samples", &H2Core::Drumkit::save_samples,
			"save a drumkit instruments samples into a directory",
			py::arg("dk_dir"),
			py::arg("overwrite"))
		.def("save_image", &H2Core::Drumkit::save_image,
			"save the drumkit image into the new directory",
			py::arg("dk_dir"),
			py::arg("overwrite"))
		.def_static("install", &H2Core::Drumkit::install,
			"install a drumkit from a filename",
			py::arg("path"))
		.def_static("remove", &H2Core::Drumkit::remove,
			"remove a drumkit from the disk",
			py::arg("dk_name"),
			py::arg("lookup"))
		.def("set_instruments", &H2Core::Drumkit::set_instruments,
			"set __instruments, delete existing one",
			py::arg("instruments"))
		.def("get_instruments", &H2Core::Drumkit::get_instruments,
			"returns #__instruments")
		.def("set_path", &H2Core::Drumkit::set_path,
			"#__path setter",
			py::arg("path"))
		.def("get_path", &H2Core::Drumkit::get_path,
			"#__path accessor")
		.def("set_name", &H2Core::Drumkit::set_name,
			"#__name setter",
			py::arg("name"))
		.def("get_name", &H2Core::Drumkit::get_name,
			"#__name accessor")
		.def("set_author", &H2Core::Drumkit::set_author,
			"#__author setter",
			py::arg("author"))
		.def("get_author", &H2Core::Drumkit::get_author,
			"#__author accessor")
		.def("set_info", &H2Core::Drumkit::set_info,
			"#__info setter",
			py::arg("info"))
		.def("get_info", &H2Core::Drumkit::get_info,
			"#__info accessor")
		.def("set_license", &H2Core::Drumkit::set_license,
			"#__license setter",
			py::arg("license"))
		.def("get_license", &H2Core::Drumkit::get_license,
			"#__license accessor")
		.def("set_image", &H2Core::Drumkit::set_image,
			"#__image setter",
			py::arg("image"))
		.def("get_image", &H2Core::Drumkit::get_image,
			"#__image accessor")
		.def("set_image_license", &H2Core::Drumkit::set_image_license,
			"#__imageLicense setter",
			py::arg("imageLicense"))
		.def("get_image_license", &H2Core::Drumkit::get_image_license,
			"#__imageLicense accessor")
		.def("samples_loaded", &H2Core::Drumkit::samples_loaded,
			"return true if the samples are loaded")
		.def("dump", &H2Core::Drumkit::dump)
		.def("isUserDrumkit", &H2Core::Drumkit::isUserDrumkit,
			"Returns Whether the associated files are located in the user or the systems drumkit folder.")
		.def("get_components", &H2Core::Drumkit::get_components)
		.def("set_components", &H2Core::Drumkit::set_components,
			py::arg("components"))
		.def("toQString", &H2Core::Drumkit::toQString,
			"Formatted string version for debugging purposes.",
			py::arg("sPrefix"),
			py::arg("bShort"));

	py::class_<H2Core::XMLNode>(m, "XMLNode")
		.def(py::init<>())
		.def(py::init<QDomNode>())
		.def_static("class_name", &H2Core::XMLNode::class_name)
		.def("createNode", &H2Core::XMLNode::createNode,
			"create a new XMLNode that has to be appended into de XMLDoc",
			py::arg("name"))
		.def("read_int", &H2Core::XMLNode::read_int,
			"reads an integer stored into a child node",
			py::arg("node"),
			py::arg("default_value"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_bool", &H2Core::XMLNode::read_bool,
			"reads a boolean stored into a child node",
			py::arg("node"),
			py::arg("default_value"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_float", py::overload_cast<const QString &, float, bool, bool>(&H2Core::XMLNode::read_float),
			"reads a float stored into a child node",
			py::arg("node"),
			py::arg("default_value"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_float", py::overload_cast<const QString &, float, bool *, bool, bool>(&H2Core::XMLNode::read_float),
			py::arg("node"),
			py::arg("default_value"),
			py::arg("pFound"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_string", &H2Core::XMLNode::read_string,
			"reads a string stored into a child node",
			py::arg("node"),
			py::arg("default_value"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_attribute", &H2Core::XMLNode::read_attribute,
			"reads an attribute from the node",
			py::arg("attribute"),
			py::arg("default_value"),
			py::arg("inexistent_ok"),
			py::arg("empty_ok"))
		.def("read_text", &H2Core::XMLNode::read_text,
			"reads the text (content) from the node",
			py::arg("empty_ok"))
		.def("write_int", &H2Core::XMLNode::write_int,
			"write an integer into a child node",
			py::arg("node"),
			py::arg("value"))
		.def("write_bool", &H2Core::XMLNode::write_bool,
			"write a boolean into a child node",
			py::arg("node"),
			py::arg("value"))
		.def("write_float", &H2Core::XMLNode::write_float,
			"write a float into a child node",
			py::arg("node"),
			py::arg("value"))
		.def("write_string", &H2Core::XMLNode::write_string,
			"write a string into a child node",
			py::arg("node"),
			py::arg("value"))
		.def("write_attribute", &H2Core::XMLNode::write_attribute,
			"write a string as an attribute of the node",
			py::arg("attribute"),
			py::arg("value"));

	py::class_<QDomNode>(m, "QDomNode")
		.def(py::init<>())
		.def(py::init<const QDomNode &>())
		.def("operator=", &QDomNode::operator=,
			py::arg(""))
		.def("operator==", &QDomNode::operator==,
			py::arg(""))
		.def("operator!=", &QDomNode::operator!=,
			py::arg(""))
		.def("insertBefore", &QDomNode::insertBefore,
			py::arg("newChild"),
			py::arg("refChild"))
		.def("insertAfter", &QDomNode::insertAfter,
			py::arg("newChild"),
			py::arg("refChild"))
		.def("replaceChild", &QDomNode::replaceChild,
			py::arg("newChild"),
			py::arg("oldChild"))
		.def("removeChild", &QDomNode::removeChild,
			py::arg("oldChild"))
		.def("appendChild", &QDomNode::appendChild,
			py::arg("newChild"))
		.def("hasChildNodes", &QDomNode::hasChildNodes)
		.def("cloneNode", &QDomNode::cloneNode,
			py::arg("deep"))
		.def("normalize", &QDomNode::normalize)
		.def("isSupported", &QDomNode::isSupported,
			py::arg("feature"),
			py::arg("version"))
		.def("nodeName", &QDomNode::nodeName)
		.def("nodeType", &QDomNode::nodeType)
		.def("parentNode", &QDomNode::parentNode)
		.def("childNodes", &QDomNode::childNodes)
		.def("firstChild", &QDomNode::firstChild)
		.def("lastChild", &QDomNode::lastChild)
		.def("previousSibling", &QDomNode::previousSibling)
		.def("nextSibling", &QDomNode::nextSibling)
		.def("attributes", &QDomNode::attributes)
		.def("ownerDocument", &QDomNode::ownerDocument)
		.def("namespaceURI", &QDomNode::namespaceURI)
		.def("localName", &QDomNode::localName)
		.def("hasAttributes", &QDomNode::hasAttributes)
		.def("nodeValue", &QDomNode::nodeValue)
		.def("setNodeValue", &QDomNode::setNodeValue,
			py::arg(""))
		.def("prefix", &QDomNode::prefix)
		.def("setPrefix", &QDomNode::setPrefix,
			py::arg("pre"))
		.def("isAttr", &QDomNode::isAttr)
		.def("isCDATASection", &QDomNode::isCDATASection)
		.def("isDocumentFragment", &QDomNode::isDocumentFragment)
		.def("isDocument", &QDomNode::isDocument)
		.def("isDocumentType", &QDomNode::isDocumentType)
		.def("isElement", &QDomNode::isElement)
		.def("isEntityReference", &QDomNode::isEntityReference)
		.def("isText", &QDomNode::isText)
		.def("isEntity", &QDomNode::isEntity)
		.def("isNotation", &QDomNode::isNotation)
		.def("isProcessingInstruction", &QDomNode::isProcessingInstruction)
		.def("isCharacterData", &QDomNode::isCharacterData)
		.def("isComment", &QDomNode::isComment)
		.def("namedItem", &QDomNode::namedItem,
			"Shortcut to avoid dealing with QDomNodeList all the time.",
			py::arg("name"))
		.def("isNull", &QDomNode::isNull)
		.def("clear", &QDomNode::clear)
		.def("toAttr", &QDomNode::toAttr)
		.def("toCDATASection", &QDomNode::toCDATASection)
		.def("toDocumentFragment", &QDomNode::toDocumentFragment)
		.def("toDocument", &QDomNode::toDocument)
		.def("toDocumentType", &QDomNode::toDocumentType)
		.def("toElement", &QDomNode::toElement)
		.def("toEntityReference", &QDomNode::toEntityReference)
		.def("toText", &QDomNode::toText)
		.def("toEntity", &QDomNode::toEntity)
		.def("toNotation", &QDomNode::toNotation)
		.def("toProcessingInstruction", &QDomNode::toProcessingInstruction)
		.def("toCharacterData", &QDomNode::toCharacterData)
		.def("toComment", &QDomNode::toComment)
		.def("save", &QDomNode::save,
			py::arg(""),
			py::arg(""),
			py::arg(""))
		.def("firstChildElement", &QDomNode::firstChildElement,
			py::arg("tagName"))
		.def("lastChildElement", &QDomNode::lastChildElement,
			py::arg("tagName"))
		.def("previousSiblingElement", &QDomNode::previousSiblingElement,
			py::arg("tagName"))
		.def("nextSiblingElement", &QDomNode::nextSiblingElement,
			py::arg("taName"))
		.def("lineNumber", &QDomNode::lineNumber)
		.def("columnNumber", &QDomNode::columnNumber);

}