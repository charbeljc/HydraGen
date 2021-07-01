#include <module.hpp>
namespace py = pybind11;

using namespace H2Core;

PYBIND11_MODULE(h2core, m) {

	py::class_<H2Core::Object> _Object(m, "Object");
	_Object.def(py::init<>());
	_Object.def(py::init<const H2Core::Object &>());
	_Object.def(py::init<const char *>());
	_Object.def("class_name", &H2Core::Object::class_name);
	_Object.def_static("set_count", &H2Core::Object::set_count,
		"enable/disable class instances counting",
		py::arg("flag"));
	_Object.def_static("count_active", &H2Core::Object::count_active);
	_Object.def_static("objects_count", &H2Core::Object::objects_count);
	// [<TypeDef 'ostream'>] _Object.def_static("write_objects_map_to", &H2Core::Object::write_objects_map_to,
		// [<TypeDef 'ostream'>] "output the full objects map to a given ostream",
		// [<TypeDef 'ostream'>] py::arg("out"),
		// [<TypeDef 'ostream'>] py::arg("map"));
	_Object.def_static("write_objects_map_to_cerr", &H2Core::Object::write_objects_map_to_cerr);
	_Object.def_static("bootstrap", &H2Core::Object::bootstrap,
		"must be called before any Object instantiation !",
		py::arg("logger"),
		py::arg("count"));
	_Object.def_static("logger", &H2Core::Object::logger);
	_Object.def_static("getAliveObjectCount", &H2Core::Object::getAliveObjectCount,
		"Returns Total numbers of objects being alive.");
	// [<TypeDef 'object_map_t'>] _Object.def_static("getObjectMap", &H2Core::Object::getObjectMap,
		// [<TypeDef 'object_map_t'>] "Returns Copy of the object map.");
	// [<TypeDef 'object_map_t'>] _Object.def_static("printObjectMapDiff", &H2Core::Object::printObjectMapDiff,
		// [<TypeDef 'object_map_t'>] "Creates the difference between a snapshot of the object map and its current state and prints it to std::cout.",
		// [<TypeDef 'object_map_t'>] py::arg("map"));
	_Object.def("toQString", &H2Core::Object::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));
	_Object.def("Print", &H2Core::Object::Print,
		"Prints content of toQString() via DEBUGLOG",
		py::arg("bShort"));

	py::class_<H2Core::Logger> _Logger(m, "Logger");
	_Logger.def_static("bootstrap", &H2Core::Logger::bootstrap,
		"create the logger instance if not exists, set the log level and return the instance",
		py::arg("msk"));
	_Logger.def_static("create_instance", &H2Core::Logger::create_instance,
		"If #__instance equals 0, a new H2Core::Logger singleton will be created and stored in it.");
	_Logger.def_static("get_instance", &H2Core::Logger::get_instance,
		"Returns a pointer to the current H2Core::Logger singleton stored in #__instance.");
	_Logger.def("should_log", &H2Core::Logger::should_log,
		"return true if the level is set in the bitmask",
		py::arg("lvl"));
	_Logger.def_static("set_bit_mask", &H2Core::Logger::set_bit_mask,
		"set the bitmask",
		py::arg("msk"));
	_Logger.def_static("bit_mask", &H2Core::Logger::bit_mask,
		"return the current log level bit mask");
	_Logger.def("set_use_file", &H2Core::Logger::set_use_file,
		"set use file flag",
		py::arg("use"));
	_Logger.def("use_file", &H2Core::Logger::use_file,
		"return __use_file");
	_Logger.def_static("parse_log_level", &H2Core::Logger::parse_log_level,
		"parse a log level string and return the corresponding bit mask",
		py::arg("lvl"));
	_Logger.def("log", &H2Core::Logger::log,
		"the log function",
		py::arg("level"),
		py::arg("class_name"),
		py::arg("func_name"),
		py::arg("msg"));

	py::class_<QDomNode> _QDomNode(m, "QDomNode");
	_QDomNode.def(py::init<>());
	_QDomNode.def(py::init<const QDomNode &>());
	_QDomNode.def("operator=", &QDomNode::operator=,
		py::arg(""));
	_QDomNode.def("operator==", &QDomNode::operator==,
		py::arg(""));
	_QDomNode.def("operator!=", &QDomNode::operator!=,
		py::arg(""));
	_QDomNode.def("insertBefore", &QDomNode::insertBefore,
		py::arg("newChild"),
		py::arg("refChild"));
	_QDomNode.def("insertAfter", &QDomNode::insertAfter,
		py::arg("newChild"),
		py::arg("refChild"));
	_QDomNode.def("replaceChild", &QDomNode::replaceChild,
		py::arg("newChild"),
		py::arg("oldChild"));
	_QDomNode.def("removeChild", &QDomNode::removeChild,
		py::arg("oldChild"));
	_QDomNode.def("appendChild", &QDomNode::appendChild,
		py::arg("newChild"));
	_QDomNode.def("hasChildNodes", &QDomNode::hasChildNodes);
	_QDomNode.def("cloneNode", &QDomNode::cloneNode,
		py::arg("deep"));
	_QDomNode.def("normalize", &QDomNode::normalize);
	_QDomNode.def("isSupported", &QDomNode::isSupported,
		py::arg("feature"),
		py::arg("version"));
	_QDomNode.def("nodeName", &QDomNode::nodeName);
	_QDomNode.def("nodeType", &QDomNode::nodeType);
	_QDomNode.def("parentNode", &QDomNode::parentNode);
	_QDomNode.def("childNodes", &QDomNode::childNodes);
	_QDomNode.def("firstChild", &QDomNode::firstChild);
	_QDomNode.def("lastChild", &QDomNode::lastChild);
	_QDomNode.def("previousSibling", &QDomNode::previousSibling);
	_QDomNode.def("nextSibling", &QDomNode::nextSibling);
	_QDomNode.def("attributes", &QDomNode::attributes);
	_QDomNode.def("ownerDocument", &QDomNode::ownerDocument);
	_QDomNode.def("namespaceURI", &QDomNode::namespaceURI);
	_QDomNode.def("localName", &QDomNode::localName);
	_QDomNode.def("hasAttributes", &QDomNode::hasAttributes);
	_QDomNode.def("nodeValue", &QDomNode::nodeValue);
	_QDomNode.def("setNodeValue", &QDomNode::setNodeValue,
		py::arg(""));
	_QDomNode.def("prefix", &QDomNode::prefix);
	_QDomNode.def("setPrefix", &QDomNode::setPrefix,
		py::arg("pre"));
	_QDomNode.def("isAttr", &QDomNode::isAttr);
	_QDomNode.def("isCDATASection", &QDomNode::isCDATASection);
	_QDomNode.def("isDocumentFragment", &QDomNode::isDocumentFragment);
	_QDomNode.def("isDocument", &QDomNode::isDocument);
	_QDomNode.def("isDocumentType", &QDomNode::isDocumentType);
	_QDomNode.def("isElement", &QDomNode::isElement);
	_QDomNode.def("isEntityReference", &QDomNode::isEntityReference);
	_QDomNode.def("isText", &QDomNode::isText);
	_QDomNode.def("isEntity", &QDomNode::isEntity);
	_QDomNode.def("isNotation", &QDomNode::isNotation);
	_QDomNode.def("isProcessingInstruction", &QDomNode::isProcessingInstruction);
	_QDomNode.def("isCharacterData", &QDomNode::isCharacterData);
	_QDomNode.def("isComment", &QDomNode::isComment);
	_QDomNode.def("namedItem", &QDomNode::namedItem,
		"Shortcut to avoid dealing with QDomNodeList all the time.",
		py::arg("name"));
	_QDomNode.def("isNull", &QDomNode::isNull);
	_QDomNode.def("clear", &QDomNode::clear);
	_QDomNode.def("toAttr", &QDomNode::toAttr);
	_QDomNode.def("toCDATASection", &QDomNode::toCDATASection);
	_QDomNode.def("toDocumentFragment", &QDomNode::toDocumentFragment);
	_QDomNode.def("toDocument", &QDomNode::toDocument);
	_QDomNode.def("toDocumentType", &QDomNode::toDocumentType);
	_QDomNode.def("toElement", &QDomNode::toElement);
	_QDomNode.def("toEntityReference", &QDomNode::toEntityReference);
	_QDomNode.def("toText", &QDomNode::toText);
	_QDomNode.def("toEntity", &QDomNode::toEntity);
	_QDomNode.def("toNotation", &QDomNode::toNotation);
	_QDomNode.def("toProcessingInstruction", &QDomNode::toProcessingInstruction);
	_QDomNode.def("toCharacterData", &QDomNode::toCharacterData);
	_QDomNode.def("toComment", &QDomNode::toComment);
	_QDomNode.def("save", &QDomNode::save,
		py::arg(""),
		py::arg(""),
		py::arg(""));
	_QDomNode.def("firstChildElement", &QDomNode::firstChildElement,
		py::arg("tagName"));
	_QDomNode.def("lastChildElement", &QDomNode::lastChildElement,
		py::arg("tagName"));
	_QDomNode.def("previousSiblingElement", &QDomNode::previousSiblingElement,
		py::arg("tagName"));
	_QDomNode.def("nextSiblingElement", &QDomNode::nextSiblingElement,
		py::arg("taName"));
	_QDomNode.def("lineNumber", &QDomNode::lineNumber);
	_QDomNode.def("columnNumber", &QDomNode::columnNumber);

	py::class_<H2Core::Filesystem> _Filesystem(m, "Filesystem");
	_Filesystem.def_static("class_name", &H2Core::Filesystem::class_name);
	_Filesystem.def_static("bootstrap", &H2Core::Filesystem::bootstrap,
		"check user and system filesystem usability",
		py::arg("logger"),
		py::arg("sys_path"));
	_Filesystem.def_static("sys_data_path", &H2Core::Filesystem::sys_data_path,
		"returns system data path");
	_Filesystem.def_static("usr_data_path", &H2Core::Filesystem::usr_data_path,
		"returns user data path");
	// [<Class 'QStringList'>] _Filesystem.def_static("ladspa_paths", &H2Core::Filesystem::ladspa_paths,
		// [<Class 'QStringList'>] "returns user ladspa paths");
	_Filesystem.def_static("sys_config_path", &H2Core::Filesystem::sys_config_path,
		"returns system config path");
	_Filesystem.def_static("usr_config_path", &H2Core::Filesystem::usr_config_path,
		"returns user config path");
	_Filesystem.def_static("empty_sample_path", &H2Core::Filesystem::empty_sample_path,
		"returns system empty sample file path");
	_Filesystem.def_static("empty_song_path", &H2Core::Filesystem::empty_song_path,
		"returns system empty song file path");
	_Filesystem.def_static("untitled_song_file_name", &H2Core::Filesystem::untitled_song_file_name,
		"returns untitled song file name");
	_Filesystem.def_static("click_file_path", &H2Core::Filesystem::click_file_path,
		"Returns a string containing the path to the _click.wav_ file used in the metronome.");
	_Filesystem.def_static("usr_click_file_path", &H2Core::Filesystem::usr_click_file_path,
		"returns click file path from user directory if exists, otherwise from system");
	_Filesystem.def_static("drumkit_xsd_path", &H2Core::Filesystem::drumkit_xsd_path,
		"returns the path to the drumkit XSD (xml schema definition) file");
	_Filesystem.def_static("pattern_xsd_path", &H2Core::Filesystem::pattern_xsd_path,
		"returns the path to the pattern XSD (xml schema definition) file");
	_Filesystem.def_static("playlist_xsd_path", &H2Core::Filesystem::playlist_xsd_path,
		"returns the path to the playlist pattern XSD (xml schema definition) file");
	_Filesystem.def_static("log_file_path", &H2Core::Filesystem::log_file_path,
		"returns the full path (including filename) of the logfile");
	_Filesystem.def_static("img_dir", &H2Core::Filesystem::img_dir,
		"returns gui image path");
	_Filesystem.def_static("doc_dir", &H2Core::Filesystem::doc_dir,
		"returns documentation path");
	_Filesystem.def_static("i18n_dir", &H2Core::Filesystem::i18n_dir,
		"returns internationalization path");
	_Filesystem.def_static("scripts_dir", &H2Core::Filesystem::scripts_dir,
		"returns user scripts path");
	_Filesystem.def_static("songs_dir", &H2Core::Filesystem::songs_dir,
		"returns user songs path");
	_Filesystem.def_static("song_path", &H2Core::Filesystem::song_path,
		"returns user song path, add file extension",
		py::arg("sg_name"));
	_Filesystem.def_static("patterns_dir_static", py::overload_cast<>(&H2Core::Filesystem::patterns_dir),
			"returns user patterns path");
	_Filesystem.def_static("patterns_dir_static", py::overload_cast<const QString &>(&H2Core::Filesystem::patterns_dir),
			"returns user patterns path for a specific drumkit",
		py::arg("dk_name"));
	_Filesystem.def_static("pattern_path", &H2Core::Filesystem::pattern_path,
		"returns user patterns path, add file extension",
		py::arg("dk_name"),
		py::arg("p_name"));
	_Filesystem.def_static("plugins_dir", &H2Core::Filesystem::plugins_dir,
		"returns user plugins path");
	_Filesystem.def_static("sys_drumkits_dir", &H2Core::Filesystem::sys_drumkits_dir,
		"returns system drumkits path");
	_Filesystem.def_static("usr_drumkits_dir", &H2Core::Filesystem::usr_drumkits_dir,
		"returns user drumkits path");
	_Filesystem.def_static("playlists_dir", &H2Core::Filesystem::playlists_dir,
		"returns user playlist path");
	_Filesystem.def_static("playlist_path", &H2Core::Filesystem::playlist_path,
		"returns user playlist path, add file extension",
		py::arg("pl_name"));
	_Filesystem.def_static("untitled_playlist_file_name", &H2Core::Filesystem::untitled_playlist_file_name,
		"returns untitled playlist file name");
	_Filesystem.def_static("cache_dir", &H2Core::Filesystem::cache_dir,
		"returns user cache path");
	_Filesystem.def_static("repositories_cache_dir", &H2Core::Filesystem::repositories_cache_dir,
		"returns user repository cache path");
	_Filesystem.def_static("demos_dir", &H2Core::Filesystem::demos_dir,
		"returns system demos path");
	_Filesystem.def_static("xsd_dir", &H2Core::Filesystem::xsd_dir,
		"returns system xsd path");
	_Filesystem.def_static("tmp_dir", &H2Core::Filesystem::tmp_dir,
		"returns temp path");
	_Filesystem.def_static("tmp_file_path", &H2Core::Filesystem::tmp_file_path,
		"touch a temporary file under tmp_dir() and return it's path. if base has a suffix it will be preserved, spaces will be replaced by underscores.",
		py::arg("base"));
	_Filesystem.def_static("prepare_sample_path", &H2Core::Filesystem::prepare_sample_path,
		"Returns the basename if the given path is under an existing user or system drumkit path, otherwise the given fname",
		py::arg("fname"));
	_Filesystem.def_static("file_is_under_drumkit", &H2Core::Filesystem::file_is_under_drumkit,
		"Checks if the given filepath is under an existing user or system drumkit path, not the existence of the file",
		py::arg("fname"));
	_Filesystem.def_static("get_basename_idx_under_drumkit", &H2Core::Filesystem::get_basename_idx_under_drumkit,
		"Returns the index of the basename if the given path is under an existing user or system drumkit path, otherwise -1",
		py::arg("fname"));
	// [<Class 'QStringList'>] _Filesystem.def_static("sys_drumkit_list", &H2Core::Filesystem::sys_drumkit_list,
		// [<Class 'QStringList'>] "returns list of usable system drumkits ( see Filesystem::drumkit_list )");
	// [<Class 'QStringList'>] _Filesystem.def_static("usr_drumkit_list", &H2Core::Filesystem::usr_drumkit_list,
		// [<Class 'QStringList'>] "returns list of usable user drumkits ( see Filesystem::drumkit_list )");
	_Filesystem.def_static("drumkit_exists", &H2Core::Filesystem::drumkit_exists,
		"returns true if the drumkit exists within usable system or user drumkits",
		py::arg("dk_name"));
	_Filesystem.def_static("drumkit_usr_path", &H2Core::Filesystem::drumkit_usr_path,
		"returns path for a drumkit within user drumkit path",
		py::arg("dk_name"));
	_Filesystem.def_static("drumkit_path_search", &H2Core::Filesystem::drumkit_path_search,
		"Returns the path to a H2Core::Drumkit folder.",
		py::arg("dk_name"),
		py::arg("lookup"),
		py::arg("bSilent"));
	_Filesystem.def_static("drumkit_dir_search", &H2Core::Filesystem::drumkit_dir_search,
		"returns the directory holding the named drumkit searching within user then system drumkits",
		py::arg("dk_name"),
		py::arg("lookup"));
	_Filesystem.def_static("drumkit_valid", &H2Core::Filesystem::drumkit_valid,
		"returns true if the path contains a usable drumkit",
		py::arg("dk_path"));
	_Filesystem.def_static("drumkit_file", &H2Core::Filesystem::drumkit_file,
		"returns the path to the xml file within a supposed drumkit path",
		py::arg("dk_path"));
	// [<Class 'QStringList'>] _Filesystem.def_static("pattern_drumkits", &H2Core::Filesystem::pattern_drumkits,
		// [<Class 'QStringList'>] "returns a list of existing drumkit sub dir into the patterns directory");
	// [<Class 'QStringList'>] _Filesystem.def_static("pattern_list_static", py::overload_cast<>(&H2Core::Filesystem::pattern_list),
			// [<Class 'QStringList'>] "returns a list of existing patterns");
	// [<Class 'QStringList'>] _Filesystem.def_static("pattern_list_static", py::overload_cast<const QString &>(&H2Core::Filesystem::pattern_list),
			// [<Class 'QStringList'>] "returns a list of existing patterns",
		// [<Class 'QStringList'>] py::arg("path"));
	// [<Class 'QStringList'>] _Filesystem.def_static("song_list", &H2Core::Filesystem::song_list,
		// [<Class 'QStringList'>] "returns a list of existing songs");
	// [<Class 'QStringList'>] _Filesystem.def_static("song_list_cleared", &H2Core::Filesystem::song_list_cleared,
		// [<Class 'QStringList'>] "returns a list of existing songs, excluding the autosaved one");
	_Filesystem.def_static("song_exists", &H2Core::Filesystem::song_exists,
		"returns true if the song file exists",
		py::arg("sg_name"));
	_Filesystem.def_static("info", &H2Core::Filesystem::info,
		"send current settings information to logger with INFO severity");
	// [<Class 'QStringList'>] _Filesystem.def_static("playlist_list", &H2Core::Filesystem::playlist_list,
		// [<Class 'QStringList'>] "returns a list of existing playlists");
	_Filesystem.def_static("file_exists", &H2Core::Filesystem::file_exists,
		"returns true if the given path is an existing regular file",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("file_readable", &H2Core::Filesystem::file_readable,
		"returns true if the given path is an existing readable regular file",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("file_writable", &H2Core::Filesystem::file_writable,
		"returns true if the given path is a possibly writable file (may exist or not)",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("file_executable", &H2Core::Filesystem::file_executable,
		"returns true if the given path is an existing executable regular file",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("dir_readable", &H2Core::Filesystem::dir_readable,
		"returns true if the given path is a readable regular directory",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("dir_writable", &H2Core::Filesystem::dir_writable,
		"returns true if the given path is a writable regular directory",
		py::arg("path"),
		py::arg("silent"));
	_Filesystem.def_static("path_usable", &H2Core::Filesystem::path_usable,
		"returns true if the path is a readable and writable regular directory, create if it not exists",
		py::arg("path"),
		py::arg("create"),
		py::arg("silent"));
	_Filesystem.def_static("write_to_file", &H2Core::Filesystem::write_to_file,
		"writes to a file",
		py::arg("dst"),
		py::arg("content"));
	_Filesystem.def_static("file_copy", &H2Core::Filesystem::file_copy,
		"copy a source file to a destination",
		py::arg("src"),
		py::arg("dst"),
		py::arg("overwrite"));
	_Filesystem.def_static("rm", &H2Core::Filesystem::rm,
		"remove a path",
		py::arg("path"),
		py::arg("recursive"));
	_Filesystem.def_static("mkdir", &H2Core::Filesystem::mkdir,
		"create a path",
		py::arg("path"));
	_Filesystem.def_static("getPreferencesOverwritePath", &H2Core::Filesystem::getPreferencesOverwritePath,
		"Returns m_sPreferencesOverwritePath");
	_Filesystem.def_static("setPreferencesOverwritePath", &H2Core::Filesystem::setPreferencesOverwritePath,
		py::arg("sPath"));

	py::class_<QDomNodeList> _QDomNodeList(m, "QDomNodeList");
	_QDomNodeList.def(py::init<>());
	_QDomNodeList.def(py::init<const QDomNodeList &>());
	_QDomNodeList.def("operator=", &QDomNodeList::operator=,
		py::arg(""));
	_QDomNodeList.def("operator==", &QDomNodeList::operator==,
		py::arg(""));
	_QDomNodeList.def("operator!=", &QDomNodeList::operator!=,
		py::arg(""));
	_QDomNodeList.def("item", &QDomNodeList::item,
		py::arg("index"));
	_QDomNodeList.def("at", &QDomNodeList::at,
		py::arg("index"));
	_QDomNodeList.def("length", &QDomNodeList::length);
	_QDomNodeList.def("count", &QDomNodeList::count);
	_QDomNodeList.def("size", &QDomNodeList::size);
	_QDomNodeList.def("isEmpty", &QDomNodeList::isEmpty);

	py::class_<QDomNamedNodeMap> _QDomNamedNodeMap(m, "QDomNamedNodeMap");
	_QDomNamedNodeMap.def(py::init<>());
	_QDomNamedNodeMap.def(py::init<const QDomNamedNodeMap &>());
	_QDomNamedNodeMap.def("operator=", &QDomNamedNodeMap::operator=,
		py::arg(""));
	_QDomNamedNodeMap.def("operator==", &QDomNamedNodeMap::operator==,
		py::arg(""));
	_QDomNamedNodeMap.def("operator!=", &QDomNamedNodeMap::operator!=,
		py::arg(""));
	_QDomNamedNodeMap.def("namedItem", &QDomNamedNodeMap::namedItem,
		py::arg("name"));
	_QDomNamedNodeMap.def("setNamedItem", &QDomNamedNodeMap::setNamedItem,
		py::arg("newNode"));
	_QDomNamedNodeMap.def("removeNamedItem", &QDomNamedNodeMap::removeNamedItem,
		py::arg("name"));
	_QDomNamedNodeMap.def("item", &QDomNamedNodeMap::item,
		py::arg("index"));
	_QDomNamedNodeMap.def("namedItemNS", &QDomNamedNodeMap::namedItemNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomNamedNodeMap.def("setNamedItemNS", &QDomNamedNodeMap::setNamedItemNS,
		py::arg("newNode"));
	_QDomNamedNodeMap.def("removeNamedItemNS", &QDomNamedNodeMap::removeNamedItemNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomNamedNodeMap.def("length", &QDomNamedNodeMap::length);
	_QDomNamedNodeMap.def("count", &QDomNamedNodeMap::count);
	_QDomNamedNodeMap.def("size", &QDomNamedNodeMap::size);
	_QDomNamedNodeMap.def("isEmpty", &QDomNamedNodeMap::isEmpty);
	_QDomNamedNodeMap.def("contains", &QDomNamedNodeMap::contains,
		py::arg("name"));

	py::class_<QTextStream> _QTextStream(m, "QTextStream");
	_QTextStream.def(py::init<>());
	_QTextStream.def(py::init<QIODevice *>());
	_QTextStream.def(py::init<FILE *, QIODevice::OpenMode>());
	_QTextStream.def(py::init<QString *, QIODevice::OpenMode>());
	_QTextStream.def(py::init<QByteArray *, QIODevice::OpenMode>());
	_QTextStream.def(py::init<const QByteArray &, QIODevice::OpenMode>());
	// [<Class 'QTextCodec'>] _QTextStream.def("setCodec", py::overload_cast<QTextCodec *>(&QTextStream::setCodec),
		// [<Class 'QTextCodec'>] py::arg("codec"));
	_QTextStream.def("setCodec", py::overload_cast<const char *>(&QTextStream::setCodec),
		py::arg("codecName"));
	// [<Class 'QTextCodec'>] _QTextStream.def("codec", &QTextStream::codec);
	_QTextStream.def("setAutoDetectUnicode", &QTextStream::setAutoDetectUnicode,
		py::arg("enabled"));
	_QTextStream.def("autoDetectUnicode", &QTextStream::autoDetectUnicode);
	_QTextStream.def("setGenerateByteOrderMark", &QTextStream::setGenerateByteOrderMark,
		py::arg("generate"));
	_QTextStream.def("generateByteOrderMark", &QTextStream::generateByteOrderMark);
	// [<Class 'QLocale'>] _QTextStream.def("setLocale", &QTextStream::setLocale,
		// [<Class 'QLocale'>] py::arg("locale"));
	// [<Class 'QLocale'>] _QTextStream.def("locale", &QTextStream::locale);
	// [<Class 'QIODevice'>] _QTextStream.def("setDevice", &QTextStream::setDevice,
		// [<Class 'QIODevice'>] py::arg("device"));
	// [<Class 'QIODevice'>] _QTextStream.def("device", &QTextStream::device);
	// [<TypeDef 'OpenMode'>] _QTextStream.def("setString", &QTextStream::setString,
		// [<TypeDef 'OpenMode'>] py::arg("string"),
		// [<TypeDef 'OpenMode'>] py::arg("openMode"));
	_QTextStream.def("string", &QTextStream::string);
	// [<Enum 'Status'>] _QTextStream.def("status", &QTextStream::status);
	// [<Enum 'Status'>] _QTextStream.def("setStatus", &QTextStream::setStatus,
		// [<Enum 'Status'>] py::arg("status"));
	_QTextStream.def("resetStatus", &QTextStream::resetStatus);
	_QTextStream.def("atEnd", &QTextStream::atEnd);
	_QTextStream.def("reset", &QTextStream::reset);
	_QTextStream.def("flush", &QTextStream::flush);
	// [<TypeDef 'qint64'>] _QTextStream.def("seek", &QTextStream::seek,
		// [<TypeDef 'qint64'>] py::arg("pos"));
	// [<TypeDef 'qint64'>] _QTextStream.def("pos", &QTextStream::pos);
	_QTextStream.def("skipWhiteSpace", &QTextStream::skipWhiteSpace);
	// [<TypeDef 'qint64'>] _QTextStream.def("readLine", &QTextStream::readLine,
		// [<TypeDef 'qint64'>] py::arg("maxlen"));
	// [<TypeDef 'qint64'>] _QTextStream.def("readLineInto", &QTextStream::readLineInto,
		// [<TypeDef 'qint64'>] py::arg("line"),
		// [<TypeDef 'qint64'>] py::arg("maxlen"));
	_QTextStream.def("readAll", &QTextStream::readAll);
	// [<TypeDef 'qint64'>] _QTextStream.def("read", &QTextStream::read,
		// [<TypeDef 'qint64'>] py::arg("maxlen"));
	// [<Enum 'FieldAlignment'>] _QTextStream.def("setFieldAlignment", &QTextStream::setFieldAlignment,
		// [<Enum 'FieldAlignment'>] py::arg("alignment"));
	// [<Enum 'FieldAlignment'>] _QTextStream.def("fieldAlignment", &QTextStream::fieldAlignment);
	// [<Class 'QChar'>] _QTextStream.def("setPadChar", &QTextStream::setPadChar,
		// [<Class 'QChar'>] py::arg("ch"));
	// [<Class 'QChar'>] _QTextStream.def("padChar", &QTextStream::padChar);
	_QTextStream.def("setFieldWidth", &QTextStream::setFieldWidth,
		py::arg("width"));
	_QTextStream.def("fieldWidth", &QTextStream::fieldWidth);
	// [<TypeDef 'NumberFlags'>] _QTextStream.def("setNumberFlags", &QTextStream::setNumberFlags,
		// [<TypeDef 'NumberFlags'>] py::arg("flags"));
	// [<TypeDef 'NumberFlags'>] _QTextStream.def("numberFlags", &QTextStream::numberFlags);
	_QTextStream.def("setIntegerBase", &QTextStream::setIntegerBase,
		py::arg("base"));
	_QTextStream.def("integerBase", &QTextStream::integerBase);
	// [<Enum 'RealNumberNotation'>] _QTextStream.def("setRealNumberNotation", &QTextStream::setRealNumberNotation,
		// [<Enum 'RealNumberNotation'>] py::arg("notation"));
	// [<Enum 'RealNumberNotation'>] _QTextStream.def("realNumberNotation", &QTextStream::realNumberNotation);
	_QTextStream.def("setRealNumberPrecision", &QTextStream::setRealNumberPrecision,
		py::arg("precision"));
	_QTextStream.def("realNumberPrecision", &QTextStream::realNumberPrecision);
	// [<Class 'QChar'>] _QTextStream.def("operator>>", py::overload_cast<QChar &>(&QTextStream::operator>>),
		// [<Class 'QChar'>] py::arg("ch"));
	_QTextStream.def("operator>>", py::overload_cast<char &>(&QTextStream::operator>>),
		py::arg("ch"));
	_QTextStream.def("operator>>", py::overload_cast<short &>(&QTextStream::operator>>),
		py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<unsigned short &>(&QTextStream::operator>>),
		py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<int &>(&QTextStream::operator>>),
		py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<unsigned int &>(&QTextStream::operator>>),
		py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<long &>(&QTextStream::operator>>),
		py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<unsigned long &>(&QTextStream::operator>>),
		py::arg("i"));
	// [<TypeDef 'qlonglong'>] _QTextStream.def("operator>>", py::overload_cast<qlonglong &>(&QTextStream::operator>>),
		// [<TypeDef 'qlonglong'>] py::arg("i"));
	// [<TypeDef 'qulonglong'>] _QTextStream.def("operator>>", py::overload_cast<qulonglong &>(&QTextStream::operator>>),
		// [<TypeDef 'qulonglong'>] py::arg("i"));
	_QTextStream.def("operator>>", py::overload_cast<float &>(&QTextStream::operator>>),
		py::arg("f"));
	_QTextStream.def("operator>>", py::overload_cast<double &>(&QTextStream::operator>>),
		py::arg("f"));
	_QTextStream.def("operator>>", py::overload_cast<QString &>(&QTextStream::operator>>),
		py::arg("s"));
	// [<Class 'QByteArray'>] _QTextStream.def("operator>>", py::overload_cast<QByteArray &>(&QTextStream::operator>>),
		// [<Class 'QByteArray'>] py::arg("array"));
	_QTextStream.def("operator>>", py::overload_cast<char *>(&QTextStream::operator>>),
		py::arg("c"));
	// [<Class 'QChar'>] _QTextStream.def("operator<<", py::overload_cast<QChar>(&QTextStream::operator<<),
		// [<Class 'QChar'>] py::arg("ch"));
	_QTextStream.def("operator<<", py::overload_cast<char>(&QTextStream::operator<<),
		py::arg("ch"));
	_QTextStream.def("operator<<", py::overload_cast<short>(&QTextStream::operator<<),
		py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<unsigned short>(&QTextStream::operator<<),
		py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<int>(&QTextStream::operator<<),
		py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<unsigned int>(&QTextStream::operator<<),
		py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<long>(&QTextStream::operator<<),
		py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<unsigned long>(&QTextStream::operator<<),
		py::arg("i"));
	// [<TypeDef 'qlonglong'>] _QTextStream.def("operator<<", py::overload_cast<qlonglong>(&QTextStream::operator<<),
		// [<TypeDef 'qlonglong'>] py::arg("i"));
	// [<TypeDef 'qulonglong'>] _QTextStream.def("operator<<", py::overload_cast<qulonglong>(&QTextStream::operator<<),
		// [<TypeDef 'qulonglong'>] py::arg("i"));
	_QTextStream.def("operator<<", py::overload_cast<float>(&QTextStream::operator<<),
		py::arg("f"));
	_QTextStream.def("operator<<", py::overload_cast<double>(&QTextStream::operator<<),
		py::arg("f"));
	_QTextStream.def("operator<<", py::overload_cast<const QString &>(&QTextStream::operator<<),
		py::arg("s"));
	// [<Class 'QStringView'>] _QTextStream.def("operator<<", py::overload_cast<QStringView>(&QTextStream::operator<<),
		// [<Class 'QStringView'>] py::arg("s"));
	// [<Class 'QLatin1String'>] _QTextStream.def("operator<<", py::overload_cast<QLatin1String>(&QTextStream::operator<<),
		// [<Class 'QLatin1String'>] py::arg("s"));
	// [<Class 'QStringRef'>] _QTextStream.def("operator<<", py::overload_cast<const QStringRef &>(&QTextStream::operator<<),
		// [<Class 'QStringRef'>] py::arg("s"));
	// [<Class 'QByteArray'>] _QTextStream.def("operator<<", py::overload_cast<const QByteArray &>(&QTextStream::operator<<),
		// [<Class 'QByteArray'>] py::arg("array"));
	_QTextStream.def("operator<<", py::overload_cast<const char *>(&QTextStream::operator<<),
		py::arg("c"));
	_QTextStream.def("operator<<", py::overload_cast<const void *>(&QTextStream::operator<<),
		py::arg("ptr"));

	py::class_<H2Core::Sample> _Sample(m, "Sample");
	_Sample.def(py::init<>());
	_Sample.def(py::init<const QString &, int, int, float *, float *>());
	_Sample.def(py::init<std::shared_ptr<Sample>>());
	_Sample.def_static("class_name", &H2Core::Sample::class_name);
	_Sample.def("write", &H2Core::Sample::write,
		"write sample to a file",
		py::arg("path"),
		py::arg("format"));
	_Sample.def_static("load_static", py::overload_cast<const QString &>(&H2Core::Sample::load),
			"Load a sample from a file.",
		py::arg("filepath"));
	// [<TemplateRef 'vector'>] _Sample.def_static("load_static", py::overload_cast<const QString &, const H2Core::Sample::Loops &, const H2Core::Sample::Rubberband &, const H2Core::Sample::VelocityEnvelope &, const H2Core::Sample::PanEnvelope &>(&H2Core::Sample::load),
			// [<TemplateRef 'vector'>] "Load a sample from a file and apply the transformations to the sample data.",
		// [<TemplateRef 'vector'>] py::arg("filepath"),
		// [<TemplateRef 'vector'>] py::arg("loops"),
		// [<TemplateRef 'vector'>] py::arg("rubber"),
		// [<TemplateRef 'vector'>] py::arg("velocity"),
		// [<TemplateRef 'vector'>] py::arg("pan"));
	_Sample.def("load", py::overload_cast<>(&H2Core::Sample::load),
			"Load the sample stored in #__filepath into #__data_l and #__data_r.");
	_Sample.def("unload", &H2Core::Sample::unload,
		"Flush the current content of the left and right channel and the current metadata.");
	// [<TemplateRef 'vector'>] _Sample.def("apply", &H2Core::Sample::apply,
		// [<TemplateRef 'vector'>] "Apply transformations to the sample data.",
		// [<TemplateRef 'vector'>] py::arg("loops"),
		// [<TemplateRef 'vector'>] py::arg("rubber"),
		// [<TemplateRef 'vector'>] py::arg("velocity"),
		// [<TemplateRef 'vector'>] py::arg("pan"));
	_Sample.def("apply_loops", &H2Core::Sample::apply_loops,
		"apply loop transformation to the sample",
		py::arg("lo"));
	// [<TemplateRef 'vector'>] _Sample.def("apply_velocity", &H2Core::Sample::apply_velocity,
		// [<TemplateRef 'vector'>] "apply velocity transformation to the sample",
		// [<TemplateRef 'vector'>] py::arg("v"));
	// [<TemplateRef 'vector'>] _Sample.def("apply_pan", &H2Core::Sample::apply_pan,
		// [<TemplateRef 'vector'>] "apply velocity transformation to the sample",
		// [<TemplateRef 'vector'>] py::arg("p"));
	_Sample.def("apply_rubberband", &H2Core::Sample::apply_rubberband,
		"apply rubberband transformation to the sample",
		py::arg("rb"));
	_Sample.def("exec_rubberband_cli", &H2Core::Sample::exec_rubberband_cli,
		"call rubberband cli to modify the sample",
		py::arg("rb"));
	_Sample.def("is_empty", &H2Core::Sample::is_empty,
		"Returns true if both data channels are null pointers");
	_Sample.def("get_filepath", &H2Core::Sample::get_filepath,
		"Returns #__filepath");
	_Sample.def("get_filename", &H2Core::Sample::get_filename,
		"Returns Filename part of #__filepath");
	_Sample.def("set_filepath", &H2Core::Sample::set_filepath,
		py::arg("filepath"));
	_Sample.def("set_filename", &H2Core::Sample::set_filename,
		py::arg("filename"));
	_Sample.def("set_frames", &H2Core::Sample::set_frames,
		"#__frames setter",
		py::arg("frames"));
	_Sample.def("get_frames", &H2Core::Sample::get_frames,
		"Returns #__frames accessor");
	_Sample.def("set_sample_rate", &H2Core::Sample::set_sample_rate,
		py::arg("sampleRate"));
	_Sample.def("get_sample_rate", &H2Core::Sample::get_sample_rate,
		"Returns #__sample_rate");
	_Sample.def("get_sample_duration", &H2Core::Sample::get_sample_duration,
		"Returns sample duration in seconds");
	_Sample.def("get_size", &H2Core::Sample::get_size,
		"Returns data size, which is calculated by #__frames time sizeof( float ) * 2");
	_Sample.def("get_data_l", &H2Core::Sample::get_data_l,
		"Returns #__data_l");
	_Sample.def("get_data_r", &H2Core::Sample::get_data_r,
		"Returns #__data_r");
	_Sample.def("set_is_modified", &H2Core::Sample::set_is_modified,
		"#__is_modified setter",
		py::arg("is_modified"));
	_Sample.def("get_is_modified", &H2Core::Sample::get_is_modified,
		"Returns #__is_modified");
	// [<TemplateRef 'vector'>] _Sample.def("get_pan_envelope", &H2Core::Sample::get_pan_envelope,
		// [<TemplateRef 'vector'>] "Returns #__pan_envelope");
	// [<TemplateRef 'vector'>] _Sample.def("get_velocity_envelope", &H2Core::Sample::get_velocity_envelope,
		// [<TemplateRef 'vector'>] "Returns #__velocity_envelope");
	_Sample.def("get_loops", &H2Core::Sample::get_loops,
		"Returns #__loops parameters");
	_Sample.def("get_rubberband", &H2Core::Sample::get_rubberband,
		"Returns #__rubberband parameters");
	_Sample.def_static("parse_loop_mode", &H2Core::Sample::parse_loop_mode,
		"parse the given string and rturn the corresponding loop_mode",
		py::arg("string"));
	_Sample.def("get_loop_mode_string", &H2Core::Sample::get_loop_mode_string,
		"Returns mode member of #__loops as a string");
	_Sample.def("toQString", &H2Core::Sample::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::InstrumentList> _InstrumentList(m, "InstrumentList");
	_InstrumentList.def(py::init<>());
	_InstrumentList.def(py::init<H2Core::InstrumentList *>());
	_InstrumentList.def_static("class_name", &H2Core::InstrumentList::class_name);
	_InstrumentList.def("size", &H2Core::InstrumentList::size,
		"returns the numbers of instruments");
	_InstrumentList.def("operator<<", &H2Core::InstrumentList::operator<<,
		"add an instrument to the list",
		py::arg("instrument"));
	_InstrumentList.def("operator[]", &H2Core::InstrumentList::operator[],
		"get an instrument from the list",
		py::arg("idx"));
	_InstrumentList.def("add", &H2Core::InstrumentList::add,
		"add an instrument to the list",
		py::arg("instrument"));
	_InstrumentList.def("insert", &H2Core::InstrumentList::insert,
		"insert an instrument into the list",
		py::arg("idx"),
		py::arg("instrument"));
	_InstrumentList.def("is_valid_index", &H2Core::InstrumentList::is_valid_index,
		"check if there is a idx is a valid index for this list without throwing an error messaage",
		py::arg("idx"));
	_InstrumentList.def("get", &H2Core::InstrumentList::get,
		"get an instrument from the list",
		py::arg("idx"));
	_InstrumentList.def("del", py::overload_cast<int>(&H2Core::InstrumentList::del),
			"remove the instrument at a given index, does not delete it",
		py::arg("idx"));
	_InstrumentList.def("del", py::overload_cast<std::shared_ptr<Instrument>>(&H2Core::InstrumentList::del),
			"remove an instrument from the list, does not delete it",
		py::arg("instrument"));
	_InstrumentList.def("index", &H2Core::InstrumentList::index,
		"get the index of an instrument within the instruments",
		py::arg("instrument"));
	_InstrumentList.def("find", py::overload_cast<const int>(&H2Core::InstrumentList::find),
			"find an instrument within the instruments",
		py::arg("i"));
	_InstrumentList.def("find", py::overload_cast<const QString &>(&H2Core::InstrumentList::find),
			"find an instrument within the instruments",
		py::arg("name"));
	_InstrumentList.def("findMidiNote", &H2Core::InstrumentList::findMidiNote,
		"find an instrument which play the given midi note",
		py::arg("note"));
	_InstrumentList.def("swap", &H2Core::InstrumentList::swap,
		"swap the instruments of two different indexes",
		py::arg("idx_a"),
		py::arg("idx_b"));
	_InstrumentList.def("move", &H2Core::InstrumentList::move,
		"move an instrument from a position to another",
		py::arg("idx_a"),
		py::arg("idx_b"));
	_InstrumentList.def("load_samples", &H2Core::InstrumentList::load_samples,
		"Calls the Instrument::load_samples() member function of all Instruments in #__instruments.");
	_InstrumentList.def("unload_samples", &H2Core::InstrumentList::unload_samples,
		"Calls the Instrument::unload_samples() member function of all Instruments in #__instruments.");
	_InstrumentList.def("save_to", &H2Core::InstrumentList::save_to,
		"save the instrument list within the given XMLNode",
		py::arg("node"),
		py::arg("component_id"));
	_InstrumentList.def_static("load_from", &H2Core::InstrumentList::load_from,
		"load an instrument list from an XMLNode",
		py::arg("node"),
		py::arg("dk_path"),
		py::arg("dk_name"));
	_InstrumentList.def("fix_issue_307", &H2Core::InstrumentList::fix_issue_307,
		"Fix GitHub issue #307, so called \"Hi Bongo fiasco\".");
	_InstrumentList.def("has_all_midi_notes_same", &H2Core::InstrumentList::has_all_midi_notes_same,
		"Check if all instruments have assigned the same MIDI out note");
	_InstrumentList.def("set_default_midi_out_notes", &H2Core::InstrumentList::set_default_midi_out_notes,
		"Set each instrument consecuteve MIDI out notes, starting from 36");
	_InstrumentList.def("toQString", &H2Core::InstrumentList::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::Instrument> _Instrument(m, "Instrument");
	_Instrument.def(py::init<const int, const QString &, std::shared_ptr<ADSR>>());
	_Instrument.def(py::init<std::shared_ptr<Instrument>>());
	_Instrument.def_static("class_name", &H2Core::Instrument::class_name);
	_Instrument.def_static("load_instrument", &H2Core::Instrument::load_instrument,
		"creates a new Instrument, loads samples from a given instrument within a given drumkit",
		py::arg("drumkit_name"),
		py::arg("instrument_name"),
		py::arg("lookup"));
	_Instrument.def("load_from", py::overload_cast<const QString &, const QString &, bool, Filesystem::Lookup>(&H2Core::Instrument::load_from),
			"loads instrument from a given instrument within a given drumkit into a `live` Instrument object.",
		py::arg("drumkit_name"),
		py::arg("instrument_name"),
		py::arg("is_live"),
		py::arg("lookup"));
	_Instrument.def("load_from", py::overload_cast<H2Core::Drumkit *, std::shared_ptr<Instrument>, bool>(&H2Core::Instrument::load_from),
			"loads instrument from a given instrument into a `live` Instrument object.",
		py::arg("drumkit"),
		py::arg("instrument"),
		py::arg("is_live"));
	_Instrument.def_static("load_from_static", py::overload_cast<H2Core::XMLNode *, const QString &, const QString &>(&H2Core::Instrument::load_from),
			"load an instrument from an XMLNode",
		py::arg("node"),
		py::arg("dk_path"),
		py::arg("dk_name"));
	_Instrument.def("load_samples", &H2Core::Instrument::load_samples,
		"Calls the InstrumentLayer::load_sample() member function of all layers of each component of the Instrument.");
	_Instrument.def("unload_samples", &H2Core::Instrument::unload_samples,
		"Calls the InstrumentLayer::unload_sample() member function of all layers of each component of the Instrument.");
	_Instrument.def("save_to", &H2Core::Instrument::save_to,
		"save the instrument within the given XMLNode",
		py::arg("node"),
		py::arg("component_id"));
	_Instrument.def("set_name", &H2Core::Instrument::set_name,
		"Sets the name of the Instrument #__name.",
		py::arg("name"));
	_Instrument.def("get_name", &H2Core::Instrument::get_name,
		"Access the name of the Instrument.");
	_Instrument.def("set_id", &H2Core::Instrument::set_id,
		"Sets #__id to id.",
		py::arg("id"));
	_Instrument.def("get_id", &H2Core::Instrument::get_id,
		"Returns #__id.");
	_Instrument.def("set_adsr", &H2Core::Instrument::set_adsr,
		"set the ADSR of the instrument",
		py::arg("adsr"));
	_Instrument.def("get_adsr", &H2Core::Instrument::get_adsr,
		"get the ADSR of the instrument");
	_Instrument.def("copy_adsr", &H2Core::Instrument::copy_adsr,
		"get a copy of the ADSR of the instrument");
	_Instrument.def("set_mute_group", &H2Core::Instrument::set_mute_group,
		"set the mute group of the instrument",
		py::arg("group"));
	_Instrument.def("get_mute_group", &H2Core::Instrument::get_mute_group,
		"get the mute group of the instrument");
	_Instrument.def("set_midi_out_channel", &H2Core::Instrument::set_midi_out_channel,
		"set the midi out channel of the instrument",
		py::arg("channel"));
	_Instrument.def("get_midi_out_channel", &H2Core::Instrument::get_midi_out_channel,
		"get the midi out channel of the instrument");
	_Instrument.def("set_midi_out_note", &H2Core::Instrument::set_midi_out_note,
		"set the midi out note of the instrument",
		py::arg("note"));
	_Instrument.def("get_midi_out_note", &H2Core::Instrument::get_midi_out_note,
		"get the midi out note of the instrument");
	_Instrument.def("set_muted", &H2Core::Instrument::set_muted,
		"set muted status of the instrument",
		py::arg("muted"));
	_Instrument.def("is_muted", &H2Core::Instrument::is_muted,
		"get muted status of the instrument");
	_Instrument.def("setPan", &H2Core::Instrument::setPan,
		"set pan of the instrument",
		py::arg("val"));
	_Instrument.def("setPanWithRangeFrom0To1", &H2Core::Instrument::setPanWithRangeFrom0To1,
		"set pan of the instrument, assuming the input range in [0;1]",
		py::arg("fVal"));
	_Instrument.def("getPan", &H2Core::Instrument::getPan,
		"get pan of the instrument");
	_Instrument.def("getPanWithRangeFrom0To1", &H2Core::Instrument::getPanWithRangeFrom0To1,
		"get pan of the instrument scaling and translating the range from [-1;1] to [0;1]");
	_Instrument.def("set_gain", &H2Core::Instrument::set_gain,
		"set gain of the instrument",
		py::arg("gain"));
	_Instrument.def("get_gain", &H2Core::Instrument::get_gain,
		"get gain of the instrument");
	_Instrument.def("set_volume", &H2Core::Instrument::set_volume,
		"set the volume of the instrument",
		py::arg("volume"));
	_Instrument.def("get_volume", &H2Core::Instrument::get_volume,
		"get the volume of the instrument");
	_Instrument.def("set_filter_active", &H2Core::Instrument::set_filter_active,
		"activate the filter of the instrument",
		py::arg("active"));
	_Instrument.def("is_filter_active", &H2Core::Instrument::is_filter_active,
		"get the status of the filter of the instrument");
	_Instrument.def("set_filter_resonance", &H2Core::Instrument::set_filter_resonance,
		"set the filter resonance of the instrument",
		py::arg("val"));
	_Instrument.def("get_filter_resonance", &H2Core::Instrument::get_filter_resonance,
		"get the filter resonance of the instrument");
	_Instrument.def("set_filter_cutoff", &H2Core::Instrument::set_filter_cutoff,
		"set the filter cutoff of the instrument",
		py::arg("val"));
	_Instrument.def("get_filter_cutoff", &H2Core::Instrument::get_filter_cutoff,
		"get the filter cutoff of the instrument");
	_Instrument.def("set_peak_l", &H2Core::Instrument::set_peak_l,
		"set the left peak of the instrument",
		py::arg("val"));
	_Instrument.def("get_peak_l", &H2Core::Instrument::get_peak_l,
		"get the left peak of the instrument");
	_Instrument.def("set_peak_r", &H2Core::Instrument::set_peak_r,
		"set the right peak of the instrument",
		py::arg("val"));
	_Instrument.def("get_peak_r", &H2Core::Instrument::get_peak_r,
		"get the right peak of the instrument");
	_Instrument.def("set_fx_level", &H2Core::Instrument::set_fx_level,
		"set the fx level of the instrument",
		py::arg("level"),
		py::arg("index"));
	_Instrument.def("get_fx_level", &H2Core::Instrument::get_fx_level,
		"get the fx level of the instrument",
		py::arg("index"));
	_Instrument.def("set_random_pitch_factor", &H2Core::Instrument::set_random_pitch_factor,
		"set the random pitch factor of the instrument",
		py::arg("val"));
	_Instrument.def("get_random_pitch_factor", &H2Core::Instrument::get_random_pitch_factor,
		"get the random pitch factor of the instrument");
	_Instrument.def("set_pitch_offset", &H2Core::Instrument::set_pitch_offset,
		"set the pitch offset of the instrument",
		py::arg("val"));
	_Instrument.def("get_pitch_offset", &H2Core::Instrument::get_pitch_offset,
		"get the pitch offset of the instrument");
	_Instrument.def("set_active", &H2Core::Instrument::set_active,
		"set the active status of the instrument",
		py::arg("active"));
	_Instrument.def("is_active", &H2Core::Instrument::is_active,
		"get the active status of the instrument");
	_Instrument.def("set_soloed", &H2Core::Instrument::set_soloed,
		"set the soloed status of the instrument",
		py::arg("soloed"));
	_Instrument.def("is_soloed", &H2Core::Instrument::is_soloed,
		"get the soloed status of the instrument");
	_Instrument.def("enqueue", &H2Core::Instrument::enqueue,
		"enqueue the instrument");
	_Instrument.def("dequeue", &H2Core::Instrument::dequeue,
		"dequeue the instrument");
	_Instrument.def("is_queued", &H2Core::Instrument::is_queued,
		"get the queued status of the instrument");
	_Instrument.def("set_stop_notes", &H2Core::Instrument::set_stop_notes,
		"set the stop notes status of the instrument",
		py::arg("stopnotes"));
	_Instrument.def("is_stop_notes", &H2Core::Instrument::is_stop_notes,
		"get the stop notes of the instrument");
	_Instrument.def("set_sample_selection_alg", &H2Core::Instrument::set_sample_selection_alg,
		py::arg("selected_algo"));
	_Instrument.def("sample_selection_alg", &H2Core::Instrument::sample_selection_alg);
	_Instrument.def("set_hihat_grp", &H2Core::Instrument::set_hihat_grp,
		py::arg("hihat_grp"));
	_Instrument.def("get_hihat_grp", &H2Core::Instrument::get_hihat_grp);
	_Instrument.def("set_lower_cc", &H2Core::Instrument::set_lower_cc,
		py::arg("message"));
	_Instrument.def("get_lower_cc", &H2Core::Instrument::get_lower_cc);
	_Instrument.def("set_higher_cc", &H2Core::Instrument::set_higher_cc,
		py::arg("message"));
	_Instrument.def("get_higher_cc", &H2Core::Instrument::get_higher_cc);
	_Instrument.def("set_drumkit_name", &H2Core::Instrument::set_drumkit_name,
		py::arg("name"));
	_Instrument.def("get_drumkit_name", &H2Core::Instrument::get_drumkit_name);
	_Instrument.def("set_is_preview_instrument", &H2Core::Instrument::set_is_preview_instrument,
		"Mark the instrument as hydrogen's preview instrument",
		py::arg("isPreview"));
	_Instrument.def("is_preview_instrument", &H2Core::Instrument::is_preview_instrument);
	_Instrument.def("set_is_metronome_instrument", &H2Core::Instrument::set_is_metronome_instrument,
		"Mark the instrument as metronome instrument",
		py::arg("isMetronome"));
	_Instrument.def("is_metronome_instrument", &H2Core::Instrument::is_metronome_instrument);
	_Instrument.def("get_components", &H2Core::Instrument::get_components);
	_Instrument.def("get_component", &H2Core::Instrument::get_component,
		py::arg("DrumkitComponentID"));
	_Instrument.def("set_apply_velocity", &H2Core::Instrument::set_apply_velocity,
		py::arg("apply_velocity"));
	_Instrument.def("get_apply_velocity", &H2Core::Instrument::get_apply_velocity);
	_Instrument.def("is_currently_exported", &H2Core::Instrument::is_currently_exported);
	_Instrument.def("set_currently_exported", &H2Core::Instrument::set_currently_exported,
		py::arg("isCurrentlyExported"));
	_Instrument.def("has_missing_samples", &H2Core::Instrument::has_missing_samples);
	_Instrument.def("set_missing_samples", &H2Core::Instrument::set_missing_samples,
		py::arg("bHasMissingSamples"));
	_Instrument.def("toQString", &H2Core::Instrument::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::InstrumentLayer> _InstrumentLayer(m, "InstrumentLayer");
	_InstrumentLayer.def(py::init<std::shared_ptr<Sample>>());
	_InstrumentLayer.def(py::init<std::shared_ptr<InstrumentLayer>>());
	_InstrumentLayer.def(py::init<std::shared_ptr<InstrumentLayer>, std::shared_ptr<Sample>>());
	_InstrumentLayer.def_static("class_name", &H2Core::InstrumentLayer::class_name);
	_InstrumentLayer.def("set_gain", &H2Core::InstrumentLayer::set_gain,
		"set the gain of the layer",
		py::arg("gain"));
	_InstrumentLayer.def("get_gain", &H2Core::InstrumentLayer::get_gain,
		"get the gain of the layer");
	_InstrumentLayer.def("set_pitch", &H2Core::InstrumentLayer::set_pitch,
		"set the pitch of the layer",
		py::arg("pitch"));
	_InstrumentLayer.def("get_pitch", &H2Core::InstrumentLayer::get_pitch,
		"get the pitch of the layer");
	_InstrumentLayer.def("set_start_velocity", &H2Core::InstrumentLayer::set_start_velocity,
		"set the start ivelocity of the layer",
		py::arg("start"));
	_InstrumentLayer.def("get_start_velocity", &H2Core::InstrumentLayer::get_start_velocity,
		"get the start velocity of the layer");
	_InstrumentLayer.def("set_end_velocity", &H2Core::InstrumentLayer::set_end_velocity,
		"set the end velocity of the layer",
		py::arg("end"));
	_InstrumentLayer.def("get_end_velocity", &H2Core::InstrumentLayer::get_end_velocity,
		"get the end velocity of the layer");
	_InstrumentLayer.def("set_sample", &H2Core::InstrumentLayer::set_sample,
		"set the sample of the layer",
		py::arg("sample"));
	_InstrumentLayer.def("get_sample", &H2Core::InstrumentLayer::get_sample,
		"get the sample of the layer");
	_InstrumentLayer.def("load_sample", &H2Core::InstrumentLayer::load_sample,
		"Calls the #H2Core::Sample::load() member function of #__sample.");
	_InstrumentLayer.def("unload_sample", &H2Core::InstrumentLayer::unload_sample);
	_InstrumentLayer.def("save_to", &H2Core::InstrumentLayer::save_to,
		"save the instrument layer within the given XMLNode",
		py::arg("node"));
	_InstrumentLayer.def_static("load_from", &H2Core::InstrumentLayer::load_from,
		"load an instrument layer from an XMLNode",
		py::arg("node"),
		py::arg("dk_path"));
	_InstrumentLayer.def("toQString", &H2Core::InstrumentLayer::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::InstrumentComponent> _InstrumentComponent(m, "InstrumentComponent");
	_InstrumentComponent.def(py::init<int>());
	_InstrumentComponent.def(py::init<std::shared_ptr<InstrumentComponent>>());
	_InstrumentComponent.def_static("class_name", &H2Core::InstrumentComponent::class_name);
	_InstrumentComponent.def("save_to", &H2Core::InstrumentComponent::save_to,
		py::arg("node"),
		py::arg("component_id"));
	_InstrumentComponent.def_static("load_from", &H2Core::InstrumentComponent::load_from,
		py::arg("node"),
		py::arg("dk_path"));
	_InstrumentComponent.def("operator[]", &H2Core::InstrumentComponent::operator[],
		py::arg("idx"));
	_InstrumentComponent.def("get_layer", &H2Core::InstrumentComponent::get_layer,
		py::arg("idx"));
	_InstrumentComponent.def("set_layer", &H2Core::InstrumentComponent::set_layer,
		py::arg("layer"),
		py::arg("idx"));
	_InstrumentComponent.def("set_drumkit_componentID", &H2Core::InstrumentComponent::set_drumkit_componentID,
		"Sets the component ID #__related_drumkit_componentID",
		py::arg("related_drumkit_componentID"));
	_InstrumentComponent.def("get_drumkit_componentID", &H2Core::InstrumentComponent::get_drumkit_componentID,
		"Returns the component ID of the drumkit.");
	_InstrumentComponent.def("set_gain", &H2Core::InstrumentComponent::set_gain,
		py::arg("gain"));
	_InstrumentComponent.def("get_gain", &H2Core::InstrumentComponent::get_gain);
	_InstrumentComponent.def_static("getMaxLayers", &H2Core::InstrumentComponent::getMaxLayers,
		"Returns #m_nMaxLayers.");
	_InstrumentComponent.def_static("setMaxLayers", &H2Core::InstrumentComponent::setMaxLayers,
		py::arg("layers"));
	_InstrumentComponent.def("toQString", &H2Core::InstrumentComponent::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::Drumkit> _Drumkit(m, "Drumkit");
	_Drumkit.def(py::init<>());
	_Drumkit.def(py::init<H2Core::Drumkit *>());
	_Drumkit.def_static("class_name", &H2Core::Drumkit::class_name);
	_Drumkit.def_static("load", &H2Core::Drumkit::load,
		"Load drumkit information from a directory.",
		py::arg("dk_dir"),
		py::arg("load_samples"));
	_Drumkit.def_static("load_by_name", &H2Core::Drumkit::load_by_name,
		"Simple wrapper for load() used with the drumkit's name instead of its directory.",
		py::arg("dk_name"),
		py::arg("load_samples"),
		py::arg("lookup"));
	_Drumkit.def_static("load_file", &H2Core::Drumkit::load_file,
		"Load a Drumkit from a file.",
		py::arg("dk_path"),
		py::arg("load_samples"));
	_Drumkit.def("load_samples", &H2Core::Drumkit::load_samples,
		"Calls the InstrumentList::load_samples() member function of #__instruments.");
	_Drumkit.def("unload_samples", &H2Core::Drumkit::unload_samples,
		"Calls the InstrumentList::unload_samples() member function of #__instruments.");
	_Drumkit.def_static("upgrade_drumkit", &H2Core::Drumkit::upgrade_drumkit,
		"Saves the current drumkit to dk_path, but makes a backup. This is used when the drumkit did not comply to our xml schema.",
		py::arg("pDrumkit"),
		py::arg("dk_path"));
	_Drumkit.def_static("user_drumkit_exists", &H2Core::Drumkit::user_drumkit_exists,
		"check if a user drumkit with the given name already exists",
		py::arg("dk_path"));
	_Drumkit.def("save", py::overload_cast<bool>(&H2Core::Drumkit::save),
			"save a drumkit, xml file and samples",
		py::arg("overwrite"));
	_Drumkit.def("save", py::overload_cast<const QString &, bool>(&H2Core::Drumkit::save),
			"save a drumkit, xml file and samples neither #__path nor #__name are updated",
		py::arg("dk_dir"),
		py::arg("overwrite"));
	_Drumkit.def_static("save_static", py::overload_cast<const QString &, const QString &, const QString &, const QString &, const QString &, const QString &, H2Core::InstrumentList *, std::vector<DrumkitComponent *> *, bool>(&H2Core::Drumkit::save),
			"save a drumkit using given parameters and an instrument list",
		py::arg("sName"),
		py::arg("sAuthor"),
		py::arg("sInfo"),
		py::arg("sLicense"),
		py::arg("sImage"),
		py::arg("sImageLicense"),
		py::arg("pInstruments"),
		py::arg("pComponents"),
		py::arg("bOverwrite"));
	_Drumkit.def("save_file", &H2Core::Drumkit::save_file,
		"save a drumkit into an xml file",
		py::arg("dk_path"),
		py::arg("overwrite"),
		py::arg("component_id"));
	_Drumkit.def("save_samples", &H2Core::Drumkit::save_samples,
		"save a drumkit instruments samples into a directory",
		py::arg("dk_dir"),
		py::arg("overwrite"));
	_Drumkit.def("save_image", &H2Core::Drumkit::save_image,
		"save the drumkit image into the new directory",
		py::arg("dk_dir"),
		py::arg("overwrite"));
	_Drumkit.def_static("install", &H2Core::Drumkit::install,
		"install a drumkit from a filename",
		py::arg("path"));
	_Drumkit.def_static("remove", &H2Core::Drumkit::remove,
		"remove a drumkit from the disk",
		py::arg("dk_name"),
		py::arg("lookup"));
	_Drumkit.def("set_instruments", &H2Core::Drumkit::set_instruments,
		"set __instruments, delete existing one",
		py::arg("instruments"));
	_Drumkit.def("get_instruments", &H2Core::Drumkit::get_instruments,
		"returns #__instruments");
	_Drumkit.def("set_path", &H2Core::Drumkit::set_path,
		"#__path setter",
		py::arg("path"));
	_Drumkit.def("get_path", &H2Core::Drumkit::get_path,
		"#__path accessor");
	_Drumkit.def("set_name", &H2Core::Drumkit::set_name,
		"#__name setter",
		py::arg("name"));
	_Drumkit.def("get_name", &H2Core::Drumkit::get_name,
		"#__name accessor");
	_Drumkit.def("set_author", &H2Core::Drumkit::set_author,
		"#__author setter",
		py::arg("author"));
	_Drumkit.def("get_author", &H2Core::Drumkit::get_author,
		"#__author accessor");
	_Drumkit.def("set_info", &H2Core::Drumkit::set_info,
		"#__info setter",
		py::arg("info"));
	_Drumkit.def("get_info", &H2Core::Drumkit::get_info,
		"#__info accessor");
	_Drumkit.def("set_license", &H2Core::Drumkit::set_license,
		"#__license setter",
		py::arg("license"));
	_Drumkit.def("get_license", &H2Core::Drumkit::get_license,
		"#__license accessor");
	_Drumkit.def("set_image", &H2Core::Drumkit::set_image,
		"#__image setter",
		py::arg("image"));
	_Drumkit.def("get_image", &H2Core::Drumkit::get_image,
		"#__image accessor");
	_Drumkit.def("set_image_license", &H2Core::Drumkit::set_image_license,
		"#__imageLicense setter",
		py::arg("imageLicense"));
	_Drumkit.def("get_image_license", &H2Core::Drumkit::get_image_license,
		"#__imageLicense accessor");
	_Drumkit.def("samples_loaded", &H2Core::Drumkit::samples_loaded,
		"return true if the samples are loaded");
	_Drumkit.def("dump", &H2Core::Drumkit::dump);
	_Drumkit.def("isUserDrumkit", &H2Core::Drumkit::isUserDrumkit,
		"Returns Whether the associated files are located in the user or the systems drumkit folder.");
	_Drumkit.def("get_components", &H2Core::Drumkit::get_components);
	_Drumkit.def("set_components", &H2Core::Drumkit::set_components,
		py::arg("components"));
	_Drumkit.def("toQString", &H2Core::Drumkit::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::ADSR> _ADSR(m, "ADSR");
	_ADSR.def(py::init<unsigned int, unsigned int, float, unsigned int>());
	_ADSR.def(py::init<const std::shared_ptr<ADSR>>());
	_ADSR.def_static("class_name", &H2Core::ADSR::class_name);
	_ADSR.def("set_attack", &H2Core::ADSR::set_attack,
		"__attack setter",
		py::arg("value"));
	_ADSR.def("get_attack", &H2Core::ADSR::get_attack,
		"__attack accessor");
	_ADSR.def("set_decay", &H2Core::ADSR::set_decay,
		"__decay setter",
		py::arg("value"));
	_ADSR.def("get_decay", &H2Core::ADSR::get_decay,
		"__decay accessor");
	_ADSR.def("set_sustain", &H2Core::ADSR::set_sustain,
		"__sustain setter",
		py::arg("value"));
	_ADSR.def("get_sustain", &H2Core::ADSR::get_sustain,
		"__sustain accessor");
	_ADSR.def("set_release", &H2Core::ADSR::set_release,
		"__release setter",
		py::arg("value"));
	_ADSR.def("get_release", &H2Core::ADSR::get_release,
		"__release accessor");
	_ADSR.def("attack", &H2Core::ADSR::attack,
		"sets state to ATTACK");
	_ADSR.def("get_value", &H2Core::ADSR::get_value,
		"compute the value and return it",
		py::arg("step"));
	_ADSR.def("release", &H2Core::ADSR::release,
		"sets state to RELEASE, returns 0 if the state is IDLE, __value if the state is RELEASE, set state to RELEASE, save __release_value and return it.");
	_ADSR.def("toQString", &H2Core::ADSR::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::DrumkitComponent> _DrumkitComponent(m, "DrumkitComponent");
	_DrumkitComponent.def(py::init<const int, const QString &>());
	_DrumkitComponent.def(py::init<H2Core::DrumkitComponent *>());
	_DrumkitComponent.def_static("class_name", &H2Core::DrumkitComponent::class_name);
	_DrumkitComponent.def("save_to", &H2Core::DrumkitComponent::save_to,
		py::arg("node"));
	_DrumkitComponent.def_static("load_from_static", py::overload_cast<H2Core::XMLNode *, const QString &>(&H2Core::DrumkitComponent::load_from),
		py::arg("node"),
		py::arg("dk_path"));
	_DrumkitComponent.def("load_from", py::overload_cast<H2Core::DrumkitComponent *, bool>(&H2Core::DrumkitComponent::load_from),
		py::arg("component"),
		py::arg("is_live"));
	_DrumkitComponent.def("set_name", &H2Core::DrumkitComponent::set_name,
		"Sets the name of the DrumkitComponent #__name.",
		py::arg("name"));
	_DrumkitComponent.def("get_name", &H2Core::DrumkitComponent::get_name,
		"Access the name of the DrumkitComponent.");
	_DrumkitComponent.def("set_id", &H2Core::DrumkitComponent::set_id,
		py::arg("id"));
	_DrumkitComponent.def("get_id", &H2Core::DrumkitComponent::get_id);
	_DrumkitComponent.def("set_volume", &H2Core::DrumkitComponent::set_volume,
		py::arg("volume"));
	_DrumkitComponent.def("get_volume", &H2Core::DrumkitComponent::get_volume);
	_DrumkitComponent.def("set_muted", &H2Core::DrumkitComponent::set_muted,
		py::arg("muted"));
	_DrumkitComponent.def("is_muted", &H2Core::DrumkitComponent::is_muted);
	_DrumkitComponent.def("set_soloed", &H2Core::DrumkitComponent::set_soloed,
		py::arg("soloed"));
	_DrumkitComponent.def("is_soloed", &H2Core::DrumkitComponent::is_soloed);
	_DrumkitComponent.def("set_peak_l", &H2Core::DrumkitComponent::set_peak_l,
		py::arg("val"));
	_DrumkitComponent.def("get_peak_l", &H2Core::DrumkitComponent::get_peak_l);
	_DrumkitComponent.def("set_peak_r", &H2Core::DrumkitComponent::set_peak_r,
		py::arg("val"));
	_DrumkitComponent.def("get_peak_r", &H2Core::DrumkitComponent::get_peak_r);
	// [<TypeDef 'uint32_t'>] _DrumkitComponent.def("reset_outs", &H2Core::DrumkitComponent::reset_outs,
		// [<TypeDef 'uint32_t'>] py::arg("nFrames"));
	_DrumkitComponent.def("set_outs", &H2Core::DrumkitComponent::set_outs,
		py::arg("nBufferPos"),
		py::arg("valL"),
		py::arg("valR"));
	_DrumkitComponent.def("get_out_L", &H2Core::DrumkitComponent::get_out_L,
		py::arg("nBufferPos"));
	_DrumkitComponent.def("get_out_R", &H2Core::DrumkitComponent::get_out_R,
		py::arg("nBufferPos"));
	_DrumkitComponent.def("toQString", &H2Core::DrumkitComponent::toQString,
		"Formatted string version for debugging purposes.",
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::XMLNode> _XMLNode(m, "XMLNode");
	_XMLNode.def(py::init<>());
	_XMLNode.def(py::init<QDomNode>());
	_XMLNode.def_static("class_name", &H2Core::XMLNode::class_name);
	_XMLNode.def("createNode", &H2Core::XMLNode::createNode,
		"create a new XMLNode that has to be appended into de XMLDoc",
		py::arg("name"));
	_XMLNode.def("read_int", &H2Core::XMLNode::read_int,
		"reads an integer stored into a child node",
		py::arg("node"),
		py::arg("default_value"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_bool", &H2Core::XMLNode::read_bool,
		"reads a boolean stored into a child node",
		py::arg("node"),
		py::arg("default_value"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_float", py::overload_cast<const QString &, float, bool, bool>(&H2Core::XMLNode::read_float),
			"reads a float stored into a child node",
		py::arg("node"),
		py::arg("default_value"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_float", py::overload_cast<const QString &, float, bool *, bool, bool>(&H2Core::XMLNode::read_float),
		py::arg("node"),
		py::arg("default_value"),
		py::arg("pFound"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_string", &H2Core::XMLNode::read_string,
		"reads a string stored into a child node",
		py::arg("node"),
		py::arg("default_value"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_attribute", &H2Core::XMLNode::read_attribute,
		"reads an attribute from the node",
		py::arg("attribute"),
		py::arg("default_value"),
		py::arg("inexistent_ok"),
		py::arg("empty_ok"));
	_XMLNode.def("read_text", &H2Core::XMLNode::read_text,
		"reads the text (content) from the node",
		py::arg("empty_ok"));
	_XMLNode.def("write_int", &H2Core::XMLNode::write_int,
		"write an integer into a child node",
		py::arg("node"),
		py::arg("value"));
	_XMLNode.def("write_bool", &H2Core::XMLNode::write_bool,
		"write a boolean into a child node",
		py::arg("node"),
		py::arg("value"));
	_XMLNode.def("write_float", &H2Core::XMLNode::write_float,
		"write a float into a child node",
		py::arg("node"),
		py::arg("value"));
	_XMLNode.def("write_string", &H2Core::XMLNode::write_string,
		"write a string into a child node",
		py::arg("node"),
		py::arg("value"));
	_XMLNode.def("write_attribute", &H2Core::XMLNode::write_attribute,
		"write a string as an attribute of the node",
		py::arg("attribute"),
		py::arg("value"));

	// enum NodeType
	py::enum_<QDomNode::NodeType>(_QDomNode, "NodeType")
		.value("ElementNode", QDomNode::NodeType::ElementNode)
		.value("AttributeNode", QDomNode::NodeType::AttributeNode)
		.value("TextNode", QDomNode::NodeType::TextNode)
		.value("CDATASectionNode", QDomNode::NodeType::CDATASectionNode)
		.value("EntityReferenceNode", QDomNode::NodeType::EntityReferenceNode)
		.value("EntityNode", QDomNode::NodeType::EntityNode)
		.value("ProcessingInstructionNode", QDomNode::NodeType::ProcessingInstructionNode)
		.value("CommentNode", QDomNode::NodeType::CommentNode)
		.value("DocumentNode", QDomNode::NodeType::DocumentNode)
		.value("DocumentTypeNode", QDomNode::NodeType::DocumentTypeNode)
		.value("DocumentFragmentNode", QDomNode::NodeType::DocumentFragmentNode)
		.value("NotationNode", QDomNode::NodeType::NotationNode)
		.value("BaseNode", QDomNode::NodeType::BaseNode)
		.value("CharacterDataNode", QDomNode::NodeType::CharacterDataNode);

	py::class_<QDomDocument> _QDomDocument(m, "QDomDocument");
	_QDomDocument.def(py::init<>());
	_QDomDocument.def(py::init<const QString &>());
	_QDomDocument.def(py::init<const QDomDocumentType &>());
	_QDomDocument.def(py::init<const QDomDocument &>());
	_QDomDocument.def("operator=", &QDomDocument::operator=,
		py::arg(""));
	_QDomDocument.def("createElement", &QDomDocument::createElement,
		py::arg("tagName"));
	_QDomDocument.def("createDocumentFragment", &QDomDocument::createDocumentFragment);
	_QDomDocument.def("createTextNode", &QDomDocument::createTextNode,
		py::arg("data"));
	_QDomDocument.def("createComment", &QDomDocument::createComment,
		py::arg("data"));
	_QDomDocument.def("createCDATASection", &QDomDocument::createCDATASection,
		py::arg("data"));
	_QDomDocument.def("createProcessingInstruction", &QDomDocument::createProcessingInstruction,
		py::arg("target"),
		py::arg("data"));
	_QDomDocument.def("createAttribute", &QDomDocument::createAttribute,
		py::arg("name"));
	_QDomDocument.def("createEntityReference", &QDomDocument::createEntityReference,
		py::arg("name"));
	_QDomDocument.def("elementsByTagName", &QDomDocument::elementsByTagName,
		py::arg("tagname"));
	_QDomDocument.def("importNode", &QDomDocument::importNode,
		py::arg("importedNode"),
		py::arg("deep"));
	_QDomDocument.def("createElementNS", &QDomDocument::createElementNS,
		py::arg("nsURI"),
		py::arg("qName"));
	_QDomDocument.def("createAttributeNS", &QDomDocument::createAttributeNS,
		py::arg("nsURI"),
		py::arg("qName"));
	_QDomDocument.def("elementsByTagNameNS", &QDomDocument::elementsByTagNameNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomDocument.def("elementById", &QDomDocument::elementById,
		py::arg("elementId"));
	_QDomDocument.def("doctype", &QDomDocument::doctype);
	// [<Class 'QDomImplementation'>] _QDomDocument.def("implementation", &QDomDocument::implementation);
	_QDomDocument.def("documentElement", &QDomDocument::documentElement);
	_QDomDocument.def("nodeType", &QDomDocument::nodeType);
	// [<Class 'QByteArray'>] _QDomDocument.def("setContent", py::overload_cast<const QByteArray &, bool, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QByteArray'>] py::arg("text"),
		// [<Class 'QByteArray'>] py::arg("namespaceProcessing"),
		// [<Class 'QByteArray'>] py::arg("errorMsg"),
		// [<Class 'QByteArray'>] py::arg("errorLine"),
		// [<Class 'QByteArray'>] py::arg("errorColumn"));
	_QDomDocument.def("setContent", py::overload_cast<const QString &, bool, QString *, int *, int *>(&QDomDocument::setContent),
		py::arg("text"),
		py::arg("namespaceProcessing"),
		py::arg("errorMsg"),
		py::arg("errorLine"),
		py::arg("errorColumn"));
	// [<Class 'QIODevice'>] _QDomDocument.def("setContent", py::overload_cast<QIODevice *, bool, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QIODevice'>] py::arg("dev"),
		// [<Class 'QIODevice'>] py::arg("namespaceProcessing"),
		// [<Class 'QIODevice'>] py::arg("errorMsg"),
		// [<Class 'QIODevice'>] py::arg("errorLine"),
		// [<Class 'QIODevice'>] py::arg("errorColumn"));
	// [<Class 'QXmlInputSource'>] _QDomDocument.def("setContent", py::overload_cast<QXmlInputSource *, bool, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QXmlInputSource'>] py::arg("source"),
		// [<Class 'QXmlInputSource'>] py::arg("namespaceProcessing"),
		// [<Class 'QXmlInputSource'>] py::arg("errorMsg"),
		// [<Class 'QXmlInputSource'>] py::arg("errorLine"),
		// [<Class 'QXmlInputSource'>] py::arg("errorColumn"));
	// [<Class 'QByteArray'>] _QDomDocument.def("setContent", py::overload_cast<const QByteArray &, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QByteArray'>] py::arg("text"),
		// [<Class 'QByteArray'>] py::arg("errorMsg"),
		// [<Class 'QByteArray'>] py::arg("errorLine"),
		// [<Class 'QByteArray'>] py::arg("errorColumn"));
	_QDomDocument.def("setContent", py::overload_cast<const QString &, QString *, int *, int *>(&QDomDocument::setContent),
		py::arg("text"),
		py::arg("errorMsg"),
		py::arg("errorLine"),
		py::arg("errorColumn"));
	// [<Class 'QIODevice'>] _QDomDocument.def("setContent", py::overload_cast<QIODevice *, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QIODevice'>] py::arg("dev"),
		// [<Class 'QIODevice'>] py::arg("errorMsg"),
		// [<Class 'QIODevice'>] py::arg("errorLine"),
		// [<Class 'QIODevice'>] py::arg("errorColumn"));
	// [<Class 'QXmlInputSource'>] _QDomDocument.def("setContent", py::overload_cast<QXmlInputSource *, QXmlReader *, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QXmlInputSource'>] py::arg("source"),
		// [<Class 'QXmlInputSource'>] py::arg("reader"),
		// [<Class 'QXmlInputSource'>] py::arg("errorMsg"),
		// [<Class 'QXmlInputSource'>] py::arg("errorLine"),
		// [<Class 'QXmlInputSource'>] py::arg("errorColumn"));
	// [<Class 'QXmlStreamReader'>] _QDomDocument.def("setContent", py::overload_cast<QXmlStreamReader *, bool, QString *, int *, int *>(&QDomDocument::setContent),
		// [<Class 'QXmlStreamReader'>] py::arg("reader"),
		// [<Class 'QXmlStreamReader'>] py::arg("namespaceProcessing"),
		// [<Class 'QXmlStreamReader'>] py::arg("errorMsg"),
		// [<Class 'QXmlStreamReader'>] py::arg("errorLine"),
		// [<Class 'QXmlStreamReader'>] py::arg("errorColumn"));
	_QDomDocument.def("toString", &QDomDocument::toString,
		py::arg(""));
	// [<Class 'QByteArray'>] _QDomDocument.def("toByteArray", &QDomDocument::toByteArray,
		// [<Class 'QByteArray'>] py::arg(""));

	py::class_<QDomAttr> _QDomAttr(m, "QDomAttr");
	_QDomAttr.def(py::init<>());
	_QDomAttr.def(py::init<const QDomAttr &>());
	_QDomAttr.def("operator=", &QDomAttr::operator=,
		py::arg(""));
	_QDomAttr.def("name", &QDomAttr::name);
	_QDomAttr.def("specified", &QDomAttr::specified);
	_QDomAttr.def("ownerElement", &QDomAttr::ownerElement);
	_QDomAttr.def("value", &QDomAttr::value);
	_QDomAttr.def("setValue", &QDomAttr::setValue,
		py::arg(""));
	_QDomAttr.def("nodeType", &QDomAttr::nodeType);

	py::class_<QDomDocumentFragment> _QDomDocumentFragment(m, "QDomDocumentFragment");
	_QDomDocumentFragment.def(py::init<>());
	_QDomDocumentFragment.def(py::init<const QDomDocumentFragment &>());
	_QDomDocumentFragment.def("operator=", &QDomDocumentFragment::operator=,
		py::arg(""));
	_QDomDocumentFragment.def("nodeType", &QDomDocumentFragment::nodeType);

	py::class_<QDomDocumentType> _QDomDocumentType(m, "QDomDocumentType");
	_QDomDocumentType.def(py::init<>());
	_QDomDocumentType.def(py::init<const QDomDocumentType &>());
	_QDomDocumentType.def("operator=", &QDomDocumentType::operator=,
		py::arg(""));
	_QDomDocumentType.def("name", &QDomDocumentType::name);
	_QDomDocumentType.def("entities", &QDomDocumentType::entities);
	_QDomDocumentType.def("notations", &QDomDocumentType::notations);
	_QDomDocumentType.def("publicId", &QDomDocumentType::publicId);
	_QDomDocumentType.def("systemId", &QDomDocumentType::systemId);
	_QDomDocumentType.def("internalSubset", &QDomDocumentType::internalSubset);
	_QDomDocumentType.def("nodeType", &QDomDocumentType::nodeType);

	py::class_<QDomElement> _QDomElement(m, "QDomElement");
	_QDomElement.def(py::init<>());
	_QDomElement.def(py::init<const QDomElement &>());
	_QDomElement.def("operator=", &QDomElement::operator=,
		py::arg(""));
	_QDomElement.def("attribute", &QDomElement::attribute,
		py::arg("name"),
		py::arg("defValue"));
	_QDomElement.def("setAttribute", py::overload_cast<const QString &, const QString &>(&QDomElement::setAttribute),
		py::arg("name"),
		py::arg("value"));
	// [<TypeDef 'qlonglong'>] _QDomElement.def("setAttribute", py::overload_cast<const QString &, qlonglong>(&QDomElement::setAttribute),
		// [<TypeDef 'qlonglong'>] py::arg("name"),
		// [<TypeDef 'qlonglong'>] py::arg("value"));
	// [<TypeDef 'qulonglong'>] _QDomElement.def("setAttribute", py::overload_cast<const QString &, qulonglong>(&QDomElement::setAttribute),
		// [<TypeDef 'qulonglong'>] py::arg("name"),
		// [<TypeDef 'qulonglong'>] py::arg("value"));
	_QDomElement.def("setAttribute", py::overload_cast<const QString &, int>(&QDomElement::setAttribute),
		py::arg("name"),
		py::arg("value"));
	// [<TypeDef 'uint'>] _QDomElement.def("setAttribute", py::overload_cast<const QString &, uint>(&QDomElement::setAttribute),
		// [<TypeDef 'uint'>] py::arg("name"),
		// [<TypeDef 'uint'>] py::arg("value"));
	_QDomElement.def("setAttribute", py::overload_cast<const QString &, float>(&QDomElement::setAttribute),
		py::arg("name"),
		py::arg("value"));
	_QDomElement.def("setAttribute", py::overload_cast<const QString &, double>(&QDomElement::setAttribute),
		py::arg("name"),
		py::arg("value"));
	_QDomElement.def("removeAttribute", &QDomElement::removeAttribute,
		py::arg("name"));
	_QDomElement.def("attributeNode", &QDomElement::attributeNode,
		py::arg("name"));
	_QDomElement.def("setAttributeNode", &QDomElement::setAttributeNode,
		py::arg("newAttr"));
	_QDomElement.def("removeAttributeNode", &QDomElement::removeAttributeNode,
		py::arg("oldAttr"));
	_QDomElement.def("elementsByTagName", &QDomElement::elementsByTagName,
		py::arg("tagname"));
	_QDomElement.def("hasAttribute", &QDomElement::hasAttribute,
		py::arg("name"));
	_QDomElement.def("attributeNS", &QDomElement::attributeNS,
		py::arg("nsURI"),
		py::arg("localName"),
		py::arg("defValue"));
	_QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, const QString &>(&QDomElement::setAttributeNS),
		py::arg("nsURI"),
		py::arg("qName"),
		py::arg("value"));
	_QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, int>(&QDomElement::setAttributeNS),
		py::arg("nsURI"),
		py::arg("qName"),
		py::arg("value"));
	// [<TypeDef 'uint'>] _QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, uint>(&QDomElement::setAttributeNS),
		// [<TypeDef 'uint'>] py::arg("nsURI"),
		// [<TypeDef 'uint'>] py::arg("qName"),
		// [<TypeDef 'uint'>] py::arg("value"));
	// [<TypeDef 'qlonglong'>] _QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, qlonglong>(&QDomElement::setAttributeNS),
		// [<TypeDef 'qlonglong'>] py::arg("nsURI"),
		// [<TypeDef 'qlonglong'>] py::arg("qName"),
		// [<TypeDef 'qlonglong'>] py::arg("value"));
	// [<TypeDef 'qulonglong'>] _QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, qulonglong>(&QDomElement::setAttributeNS),
		// [<TypeDef 'qulonglong'>] py::arg("nsURI"),
		// [<TypeDef 'qulonglong'>] py::arg("qName"),
		// [<TypeDef 'qulonglong'>] py::arg("value"));
	_QDomElement.def("setAttributeNS", py::overload_cast<const QString, const QString &, double>(&QDomElement::setAttributeNS),
		py::arg("nsURI"),
		py::arg("qName"),
		py::arg("value"));
	_QDomElement.def("removeAttributeNS", &QDomElement::removeAttributeNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomElement.def("attributeNodeNS", &QDomElement::attributeNodeNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomElement.def("setAttributeNodeNS", &QDomElement::setAttributeNodeNS,
		py::arg("newAttr"));
	_QDomElement.def("elementsByTagNameNS", &QDomElement::elementsByTagNameNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomElement.def("hasAttributeNS", &QDomElement::hasAttributeNS,
		py::arg("nsURI"),
		py::arg("localName"));
	_QDomElement.def("tagName", &QDomElement::tagName);
	_QDomElement.def("setTagName", &QDomElement::setTagName,
		py::arg("name"));
	_QDomElement.def("attributes", &QDomElement::attributes);
	_QDomElement.def("nodeType", &QDomElement::nodeType);
	_QDomElement.def("text", &QDomElement::text);

	py::class_<QDomEntityReference> _QDomEntityReference(m, "QDomEntityReference");
	_QDomEntityReference.def(py::init<>());
	_QDomEntityReference.def(py::init<const QDomEntityReference &>());
	_QDomEntityReference.def("operator=", &QDomEntityReference::operator=,
		py::arg(""));
	_QDomEntityReference.def("nodeType", &QDomEntityReference::nodeType);

	py::class_<QDomEntity> _QDomEntity(m, "QDomEntity");
	_QDomEntity.def(py::init<>());
	_QDomEntity.def(py::init<const QDomEntity &>());
	_QDomEntity.def("operator=", &QDomEntity::operator=,
		py::arg(""));
	_QDomEntity.def("publicId", &QDomEntity::publicId);
	_QDomEntity.def("systemId", &QDomEntity::systemId);
	_QDomEntity.def("notationName", &QDomEntity::notationName);
	_QDomEntity.def("nodeType", &QDomEntity::nodeType);

	py::class_<QDomNotation> _QDomNotation(m, "QDomNotation");
	_QDomNotation.def(py::init<>());
	_QDomNotation.def(py::init<const QDomNotation &>());
	_QDomNotation.def("operator=", &QDomNotation::operator=,
		py::arg(""));
	_QDomNotation.def("publicId", &QDomNotation::publicId);
	_QDomNotation.def("systemId", &QDomNotation::systemId);
	_QDomNotation.def("nodeType", &QDomNotation::nodeType);

	py::class_<QDomProcessingInstruction> _QDomProcessingInstruction(m, "QDomProcessingInstruction");
	_QDomProcessingInstruction.def(py::init<>());
	_QDomProcessingInstruction.def(py::init<const QDomProcessingInstruction &>());
	_QDomProcessingInstruction.def("operator=", &QDomProcessingInstruction::operator=,
		py::arg(""));
	_QDomProcessingInstruction.def("target", &QDomProcessingInstruction::target);
	_QDomProcessingInstruction.def("data", &QDomProcessingInstruction::data);
	_QDomProcessingInstruction.def("setData", &QDomProcessingInstruction::setData,
		py::arg("d"));
	_QDomProcessingInstruction.def("nodeType", &QDomProcessingInstruction::nodeType);

	py::class_<QDomCharacterData> _QDomCharacterData(m, "QDomCharacterData");
	_QDomCharacterData.def(py::init<>());
	_QDomCharacterData.def(py::init<const QDomCharacterData &>());
	_QDomCharacterData.def("operator=", &QDomCharacterData::operator=,
		py::arg(""));
	_QDomCharacterData.def("substringData", &QDomCharacterData::substringData,
		py::arg("offset"),
		py::arg("count"));
	_QDomCharacterData.def("appendData", &QDomCharacterData::appendData,
		py::arg("arg"));
	_QDomCharacterData.def("insertData", &QDomCharacterData::insertData,
		py::arg("offset"),
		py::arg("arg"));
	_QDomCharacterData.def("deleteData", &QDomCharacterData::deleteData,
		py::arg("offset"),
		py::arg("count"));
	_QDomCharacterData.def("replaceData", &QDomCharacterData::replaceData,
		py::arg("offset"),
		py::arg("count"),
		py::arg("arg"));
	_QDomCharacterData.def("length", &QDomCharacterData::length);
	_QDomCharacterData.def("data", &QDomCharacterData::data);
	_QDomCharacterData.def("setData", &QDomCharacterData::setData,
		py::arg(""));
	_QDomCharacterData.def("nodeType", &QDomCharacterData::nodeType);

	// enum EncodingPolicy
	py::enum_<QDomNode::EncodingPolicy>(_QDomNode, "EncodingPolicy")
		.value("EncodingFromDocument", QDomNode::EncodingPolicy::EncodingFromDocument)
		.value("EncodingFromTextStream", QDomNode::EncodingPolicy::EncodingFromTextStream);

	// enum Lookup
	py::enum_<H2Core::Filesystem::Lookup>(_Filesystem, "Lookup")
		.value("stacked", H2Core::Filesystem::Lookup::stacked)
		.value("user", H2Core::Filesystem::Lookup::user)
		.value("system", H2Core::Filesystem::Lookup::system);

	py::class_<H2Core::Sample::Loops> _Loops(m, "Loops");
	_Loops.def(py::init<>());
	_Loops.def(py::init<const H2Core::Sample::Loops *>());
	_Loops.def("operator==", &H2Core::Sample::Loops::operator==,
		"equal to operator",
		py::arg("b"));
	_Loops.def("toQString", &H2Core::Sample::Loops::toQString,
		py::arg("sPrefix"),
		py::arg("bShort"));

	py::class_<H2Core::Sample::Rubberband> _Rubberband(m, "Rubberband");
	_Rubberband.def(py::init<>());
	_Rubberband.def(py::init<const H2Core::Sample::Rubberband *>());
	_Rubberband.def("operator==", &H2Core::Sample::Rubberband::operator==,
		"equal to operator",
		py::arg("b"));
	_Rubberband.def("toQString", &H2Core::Sample::Rubberband::toQString,
		py::arg("sPrefix"),
		py::arg("bShort"));

	// enum SampleSelectionAlgo
	py::enum_<H2Core::Instrument::SampleSelectionAlgo>(_Instrument, "SampleSelectionAlgo")
		.value("VELOCITY", H2Core::Instrument::SampleSelectionAlgo::VELOCITY)
		.value("ROUND_ROBIN", H2Core::Instrument::SampleSelectionAlgo::ROUND_ROBIN)
		.value("RANDOM", H2Core::Instrument::SampleSelectionAlgo::RANDOM);

	py::class_<QDomText> _QDomText(m, "QDomText");
	_QDomText.def(py::init<>());
	_QDomText.def(py::init<const QDomText &>());
	_QDomText.def("operator=", &QDomText::operator=,
		py::arg(""));
	_QDomText.def("splitText", &QDomText::splitText,
		py::arg("offset"));
	_QDomText.def("nodeType", &QDomText::nodeType);

	py::class_<QDomComment> _QDomComment(m, "QDomComment");
	_QDomComment.def(py::init<>());
	_QDomComment.def(py::init<const QDomComment &>());
	_QDomComment.def("operator=", &QDomComment::operator=,
		py::arg(""));
	_QDomComment.def("nodeType", &QDomComment::nodeType);

	// enum LoopMode
	py::enum_<H2Core::Sample::Loops::LoopMode>(_Loops, "LoopMode")
		.value("FORWARD", H2Core::Sample::Loops::LoopMode::FORWARD)
		.value("REVERSE", H2Core::Sample::Loops::LoopMode::REVERSE)
		.value("PINGPONG", H2Core::Sample::Loops::LoopMode::PINGPONG);

	py::class_<QDomCDATASection> _QDomCDATASection(m, "QDomCDATASection");
	_QDomCDATASection.def(py::init<>());
	_QDomCDATASection.def(py::init<const QDomCDATASection &>());
	_QDomCDATASection.def("operator=", &QDomCDATASection::operator=,
		py::arg(""));
	_QDomCDATASection.def("nodeType", &QDomCDATASection::nodeType);

}