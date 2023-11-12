#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <iostream>

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
    try{
        if(number == 0.0f){
            throw(number);
        }
        else{
            result = 1.0f/number;
        }
    }catch(float n){
        std::cout << "division par " << n << " impossible" << std::endl;
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
