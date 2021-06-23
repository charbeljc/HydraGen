cmake_minimum_required(VERSION 3.4...3.18)
project(bindingtests)
find_package(Qt5Core REQUIRED)
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_program(binder binder REQUIRED)

set(bindings_library "bindtest")
set(CMAKE_AUTOMOC OFF)
set(CMAKE_AUTOUIC OFF)

set(wrapped_header ${CMAKE_CURRENT_SOURCE_DIR}/bindings.h)
set(config_file ${CMAKE_CURRENT_SOURCE_DIR}/bindings.conf)
set(sources_dependencies ${wrapped_header} ${config_file})
set(binder_options 
    -c -fPIC -std=c++14
    -I/usr/include/c++/10/
    -I/usr/include/x86_64-linux-gnu/c++/10/
    -I/usr/include/x86_64-linux-gnu/qt5/
    -I/usr/include/x86_64-linux-gnu/qt5/QtCore
    -I/usr/include/x86_64-linux-gnu/qt5/QtGui
    -I/usr/include/x86_64-linux-gnu/qt5/QtXml
    -I${CMAKE_CURRENT_SOURCE_DIR}
)
set(binder_outdir ${CMAKE_CURRENT_SOURCE_DIR})
set(binder_namespace bindtest)
# Add custom target to run binder to generate the binding cpp files.
set(sources
${binder_outdir}/out/test_qstring.cpp
)
# file(GLOB_RECURSE sources *.cpp)

add_custom_command(OUTPUT ${sources}
                    COMMAND ${binder}
                    --trace
                    -v
                    # --flat
                    --annotate-includes
                    --config ${config_file}
                    --root-module ${bindings_library}/out
                    --prefix ${CMAKE_CURRENT_SOURCE_DIR}/
                    --bind ${binder_namespace} # namespace to build
                    ${wrapped_header}
                    -- ${binder_options}
                    DEPENDS ${wrapped_header} ${config_file}
                    IMPLICIT_DEPENDS CXX ${wrapped_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${bindings_library}.")

add_library(${bindings_library} MODULE ${sources})
target_link_libraries(${bindings_library} PRIVATE
    pybind11::module pybind11::lto pybind11::windows_extras
	Qt5::Core
)

target_include_directories(${bindings_library} PRIVATE
    ${QT_INCLUDES}
# Apply relevant include and link flags.
${python_include_dir}
${CMAKE_CURRENT_SOURCE_DIR}
)

pybind11_extension(${bindings_library})
