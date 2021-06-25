cmake_minimum_required(VERSION 3.4...3.18)
project(bindingtests)
find_package(Qt5 COMPONENTS Core REQUIRED)
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_program(binder binder REQUIRED)

set(bindings_library "bindtest")
set(CMAKE_AUTOMOC OFF)
set(CMAKE_AUTOUIC OFF)
message("ns? ${USE_NAMESPACE}")
set(wrapped_header ${CMAKE_CURRENT_SOURCE_DIR}/bindings.h)
set(config_file ${CMAKE_CURRENT_SOURCE_DIR}/bindings.conf)
set(sources_dependencies ${wrapped_header} ${config_file})
if(USE_NAMESPACE)
    set(additional -DUSE_NAMESPACE=1)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DUSE_NAMESPACE=1")
    set(namespace "test")
else()
    set(namespace "")
endif()
set(binder_options 
    -x c++ -c -fPIC -std=c++14 -fexceptions
    ${additional}
    -I/usr/include/c++/10/
    -I/usr/include/x86_64-linux-gnu/c++/10/
    -I/usr/include/x86_64-linux-gnu/qt5/
    -I/usr/include/x86_64-linux-gnu/qt5/QtCore
    -I/usr/include/x86_64-linux-gnu/qt5/QtGui
    -I/usr/include/x86_64-linux-gnu/qt5/QtXml
    -I${CMAKE_CURRENT_SOURCE_DIR}
)
set(binder_outdir ${CMAKE_CURRENT_SOURCE_DIR}/out)
set(binder_namespace bindtest)
# Add custom target to run binder to generate the binding cpp files.
set(sources
${CMAKE_CURRENT_SOURCE_DIR}/test_qstring.cpp
)
set(generated_sources
${binder_outdir}/${bindings_library}.cpp
${binder_outdir}/singleton.cpp
${binder_outdir}/test_qstring.cpp
)
# file(GLOB_RECURSE sources *.cpp)

add_custom_command(OUTPUT ${generated_sources}
                    COMMAND ${binder}
                    --trace
                    -v
                    # --flat
                    --annotate-includes
                    --config ${config_file}
                    --root-module ${bindings_library}
                    --prefix ${binder_outdir}
                    --bind \"${namespace}\" # namespace to build
                    ${wrapped_header}
                    -- ${binder_options}
                    DEPENDS ${wrapped_header} ${config_file}
                    IMPLICIT_DEPENDS CXX ${wrapped_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${bindings_library}.")

add_library(${bindings_library} MODULE ${sources} ${generated_sources})
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
