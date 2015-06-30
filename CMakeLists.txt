# Minimum version of CMake required
cmake_minimum_required (VERSION 3.0.2)
set(CMAKE_MACOSX_RPATH 0)

project(IGTLinkPython)

# Install

install(FILES "${PROJECT_SOURCE_DIR}/code/IGTLink.py" DESTINATION ${INSTALL_PATH}/bin)