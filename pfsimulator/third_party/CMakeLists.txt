
add_subdirectory (cjson)
add_subdirectory (etrace)


#
# External Project for argparse
#
ExternalProject_Add(argparse_project
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/argparse
  BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}/argparse"
  CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}
  BUILD_COMMAND ${CMAKE_COMMAND} --build <BINARY_DIR>
  INSTALL_COMMAND ${CMAKE_COMMAND} --build <BINARY_DIR> --target install
  UPDATE_DISCONNECTED 1
  )

add_library(argparse INTERFACE IMPORTED GLOBAL)

# This is needed since INTERFACE_INCLUDE_DIRECTORIES is checked so must exist at configure time
# Tried to use generator expression but that didn't work
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/include)
set_property(TARGET argparse PROPERTY IMPORTED_LOCATION ${CMAKE_INSTALL_PREFIX}/lib64/libargparse.so)
set_property(TARGET argparse PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${CMAKE_INSTALL_PREFIX}/include)


