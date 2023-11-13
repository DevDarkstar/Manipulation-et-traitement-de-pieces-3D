#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <iostream>
#include <stdexcept>

namespace py = pybind11;

int getVerticesNumber(const std::vector<std::vector<double>>& data){
    return (int)data.size();
}

int getEdgesNumber(const std::vector<std::vector<double>>& data){
    return (int)data.size();
}

int getFacesNumber(const std::vector<std::vector<double>>& data){
    return (int)data.size();
}

float testDivideByNumber(float number){
    float result = 0.0f;
    if(number == 0.0f){
        throw std::runtime_error("Impossible de diviser un nombre par " + std::to_string(number));
    }
    else{
        result = 1.0f/number;
    }
    return result;
}

PYBIND11_MODULE(count_objects, handle){
    handle.doc() = "compte le nombre de sommets, arêtes et faces d'un objet géométrique";
    handle.def("getVerticesNumber", &getVerticesNumber);
    handle.def("getEdgesNumber", &getEdgesNumber);
    handle.def("getFacesNumber", &getFacesNumber);
    handle.def("testDivideByNumber", &testDivideByNumber);
}