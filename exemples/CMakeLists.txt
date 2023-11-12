cmake_minimum_required(VERSION 3.2)
project(test_pybind11)
add_subdirectory(pybind11)
pybind11_add_module(test count_objects.cpp)
