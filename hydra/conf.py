from __future__ import annotations, barry_as_FLUFL

import pathlib
import sys
from collections import abc
from pathlib import Path

import yaml
from logzero import logger
from orderedset import OrderedSet


class Config:
    """Config object holding all aspects binding generation"""

    _banned: set[str]
    _banned_patterns: set[str]
    _cleaners: set[str]
    _plugins: set[str]
    _include_path: set[Path]
    _clags: set[str]
    _lambdas: dict[str, dict[str, str]]
    _addon_methods: dict[str, dict[str, str]]
    _policies: dict[str, str]
    _emit_fields: bool = True
    _emit_methods: bool = True
    _emit_ctors: bool = True
    _emit_dtors: bool = True
    _prolog: set[str]
    _module_name: str
    _bindings: dict[str, list[str | Path]]
    _exported_enum_values: set[str]
    _arith_enums: set[str]

    def __init__(self, modname: str):
        self._module_name = modname
        self._banned = OrderedSet()
        self._banned_patterns = OrderedSet()
        self._banned_prefixes = OrderedSet()
        self._banned_suffixes = OrderedSet()
        self._cleaners = OrderedSet()
        self._plugins = OrderedSet()
        self._cflags = OrderedSet()
        self._include_path = OrderedSet()
        self._lambdas = dict()
        self._addon_methods = dict()
        self._policies = dict()
        self._prolog = OrderedSet()
        self._bindings = dict()
        self._exported_enum_values = OrderedSet()
        self._arith_enums = OrderedSet()

    @staticmethod
    def parse(path: str) -> Config:
        with open(path) as src:
            data = yaml.safe_load(src)
        module_data = data['module']

        conf = Config(module_data["name"])
        conf.add_cflags(module_data["flags"])
        for path in module_data["include_path"]:
            conf.add_include_path(path)
        conf._bindings = module_data["bindings"]

        if 'ban' in module_data:
            conf.ban(module_data["ban"])

        if 'cleaners' in module_data:
            for cleaner in module_data["cleaners"]:
                conf.add_cleaner(cleaner)

        if 'plugins' in module_data:
            for plugin in module_data["plugins"]:
                conf.add_plugin(plugin)

        if 'policies' in module_data:
            for policy in module_data["policies"]:
                conf.add_policy(policy["name"], policy["policy"])

        if 'prolog' in module_data:
            conf.add_prolog(module_data["prolog"])

        if 'bind_with_lambda' in module_data:
            for item in module_data["bind_with_lambda"]:
                qname, *sig = item["name"].split("(", 1)
                *parent, name = qname.split("::")
                assert parent
                parent = "::".join(parent)
                assert sig
                fun = name + "(" + sig[0]
                conf.bind_with_lambda(parent, fun, item["code"])
        if 'add_method' in module_data:
            for item in module_data["add_method"]:
                qname, *sig = item["name"].split("(", 1)
                *parent, name = qname.split("::")
                assert parent
                parent = "::".join(parent)
                assert not sig
                # fun = name + '(' + sig[0]
                conf.add_method(parent, name, item["code"])
        if 'export_enum_values' in module_data:
            conf.export_enum_values(module_data['export_enum_values'])
        if 'arith_enum' in module_data:
            conf.add_arith_enum(module_data['arith_enum'])

        return conf

    def ban(self, spec: str | list[str]) -> Config:
        """
        ban a given `cppname` from genarated bindings.

        `cppname` must be a fully qualified name, with optional signature, eg:

        >>> config = (Config()
        ...           .ban("QtPrivate")  # ban whole namespace
        ...           "QColor::QColor(QColor &&)",  # ban this constructor
        ...           "QColor::name",  # ban whole method, regardless of overloaded signatures
        ...           "QColor::operator=",
        ...           "QDomNodePrivate",
        ... )
        """
        if isinstance(spec, str):
            spec = [spec]
        for cppname in spec:
            if cppname.startswith("*::"):
                self._banned_patterns.add(cppname[3:])
            elif cppname.startswith("*"):
                self._banned_suffixes.add(cppname[1:])
            elif cppname.endswith("*") and not cppname.endswith('operator*'):
                self._banned_prefixes.add(cppname[:-1])
            else:
                self._banned.add(cppname)
        return self

    def add_include_path(self, path: str | Path) -> Config:
        path = Path(path)
        if not path.exists():
            raise ValueError("path not found: %r" % path)
        path = path.absolute()
        self._include_path.add(path)
        return self

    def add_cleaner(self, include) -> Config:
        if not self._check_include(include):
            raise ValueError("%s not found in include path" % include)
        self._cleaners.add(include)
        return self

    def add_plugin(self, include) -> Config:
        if not self._check_include(include):
            raise ValueError("%s not found in include path" % include)
        self._plugins.add(include)
        return self

    def add_cflag(self, flag: str) -> Config:
        flag = flag.strip()
        if flag:
            if flag.startswith("-I"):
                logger.warning(
                    "Config.add_cflag() should not be used with %r, "
                    "use Config.add_include_path() instead",
                    flag,
                )
                flag = flag[2:].strip()
                self.add_include_path(flag)
            else:
                self._cflags.add(flag)
        return self

    def add_cflags(self, flags: str | list[str]) -> Config:
        if isinstance(flags, str):
            flags = flags.split()
        for flag in flags:
            self.add_cflag(flag)
        return self

    def bind_with_lambda(self, fqr: str, signature: str, code: str) -> Config:
        self._lambdas.setdefault(fqr, dict())[signature] = code
        return self

    def add_method(self, fqr: str, name: str, code: str) -> Config:
        self._addon_methods.setdefault(fqr, dict())[name] = code
        return self

    def add_policy(self, signature: str, policy: str) -> Config:
        self._policies[signature] = policy
        return self

    def add_prolog(self, code) -> Config:
        self._prolog.add(code)
        return self
    
    def export_enum_values(self, spec: str | list[str]) -> Config:
        if isinstance(spec, str):
            spec = list(spec)
        for name in spec:
            self._exported_enum_values.add(name)
        return self

    def are_enum_values_exported(self, name) -> bool:
        return name in self._exported_enum_values

    def add_arith_enum(self, spec: str | list[str]) -> Config:
        if isinstance(spec, str):
            spec = list(spec)
        for name in spec:
            self._arith_enums.add(name)
        return self

    def arith_enum(self, name) -> bool:
        return name in self._arith_enums

    def emit(self, what) -> Config:
        for key in what:
            setattr(self, f"_emit_{key}", what[key])
        return self

    def _check_include(self, include):
        for path in self._include_path:
            if path.joinpath(include).exists():
                return True
        return False

    def is_banned(self, cppname):
        """check if a given cppname is banned from bindings generation"""
        banned = False
        if cppname in self._banned:
            return True

        if '(' in cppname:
            fullname, signature = cppname.split("(", 1)
            signature = "(" + signature
        else:
            fullname, signature = cppname, ""

        if '&&' in signature:  # pybind11 always barks on this
            return True

        if "::" in fullname:
            last = fullname.split("::")[-1]
            localname = last + signature
            if localname in self._banned_patterns:
                banned = True
        else:
            localname = last = fullname

        for sfx in self._banned_suffixes:
            if fullname.endswith(sfx):
                banned = True
                break

        for pfx in self._banned_prefixes:
            if fullname.startswith(pfx):
                banned = True
                break
            if localname.startwith(pfx):
                banned = True
                break

        return banned

    def dump(self, file=None):
        if file is None:
            file = sys.stderr
        print("banned", file=file)
        for ban in self._banned:
            print("\t", ban, file=file)

        print("banned pattern", file=file)
        for ban in self._banned_patterns:
            print("\t", ban, file=file)

        print("include path", file=file)
        for path in self._include_path:
            print("\t", path, file=file)

        print("clags", file=file)
        print("\t", " ".join(self._cflags), file=file)
        print("cleaners", file=file)
        for path in self.cleaners:
            print("\t", path, file=file)
        print("plugins", file=file)
        for path in self.plugins:
            print("\t", path, file=file)

    @property
    def cleaners(self) -> list[str]:
        return list(self._cleaners)

    @property
    def plugins(self) -> list[str]:
        return list(self._plugins)

    @property
    def include_path(self) -> list[Path]:
        return list(self._include_path)

    @property
    def cflags(self) -> list[str]:
        return list(self._cflags)
