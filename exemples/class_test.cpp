#include "class_test.hpp"
#include <pybind11/pybind11.h>

namespace py = pybind11;

template <class T>
Class_test<T>::Class_test() : m_a(0), m_b(0){}

template <class T>
Class_test<T>::Class_test(T a, T b) : m_a(a), m_b(b){}

template <class T>
T Class_test<T>::multiplier(){
    return m_a * m_b;
}

PYBIND11_MODULE(class_test, handle){
    handle.doc() = "Exemple avec une classe";

    py::class_<Class_test<int>>(handle, "Class_test_Int")
        .def(py::init())
        .def(py::init<int, int>())
        .def("multiplier", &Class_test<int>::multiplier);

    py::class_<Class_test<float>>(handle, "Class_test_Float")
        .def(py::init())
        .def(py::init<float, float>())
        .def("multiplier", &Class_test<float>::multiplier);
}
