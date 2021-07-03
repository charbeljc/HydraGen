from setuptools import _install_setup_requires, setup

setup(name='hydragen',
      version='0.1.0',
      packages=['hydra'],
      install_requires=['logzero', 'orderedset', 'clang', 'PyYAML', 'pybind11']
)

