# Created by the script cgal_create_CMakeLists
# This is the CMake script for compiling a set of CGAL applications.

cmake_minimum_required(VERSION 3.1...3.23)

project( mesh_segmentation )
# Les deux lignes suivantes permettant d'ajouter le module Pybind11 à la compilation
add_subdirectory(pybind11)
pybind11_add_module(surface_mesh_segmentation SurfaceMeshSegmentation.cpp)


# CGAL and its components
find_package( CGAL QUIET COMPONENTS  )
# Les deux lignes suivantes sont à ajouter en plus au fichier CMakeLists généré par CGAL
include(${CGAL_USE_FILE})
include_directories(${Boost_INCLUDE_DIRS})

if ( NOT CGAL_FOUND )

  message(STATUS "This project requires the CGAL library, and will not be compiled.")
  return()  

endif()


# Boost and its components
find_package( Boost REQUIRED )

if ( NOT Boost_FOUND )

  message(STATUS "This project requires the Boost library, and will not be compiled.")

  return()  

endif()

# include for local directory

# include for local package


# Creating entries for all C++ files with "main" routine
# ##########################################################




