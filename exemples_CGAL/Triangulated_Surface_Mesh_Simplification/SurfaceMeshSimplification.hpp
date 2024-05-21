#ifndef SURFACEMESHSIMPLIFICATION_HPP
#define SURFACEMESHSIMPLIFICATION_HPP

#include <vector>
#include <chrono>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <stdexcept>
#include <algorithm>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Surface_mesh_simplification/edge_collapse.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Edge_count_ratio_stop_predicate.h>
#include <CGAL/boost/graph/generators.h>

typedef CGAL::Simple_cartesian<double>          Kernel;
typedef Kernel::Point_3                         Point_3;
typedef CGAL::Surface_mesh<Point_3>             Surface_mesh;
typedef Surface_mesh::Vertex_index              vertex_descriptor;
typedef Surface_mesh::Face_index                face_descriptor;

class SurfaceMeshSimplification{
    public:
    explicit SurfaceMeshSimplification(pybind11::dict data);
    void triangulated_surface_mesh_simplification();
    void update_vertices_coordinates();
    pybind11::dict get_surface_mesh_data();
    void update_face_indices();
    std::unordered_map<vertex_descriptor, int> get_indices_remapping();

    private:
    Surface_mesh m_surface_mesh;
    pybind11::dict m_surface_mesh_data;
    double m_stop_ratio;
};

#endif
