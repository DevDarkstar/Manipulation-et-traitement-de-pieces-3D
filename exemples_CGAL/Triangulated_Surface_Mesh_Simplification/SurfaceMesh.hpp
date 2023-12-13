#ifndef SURFACEMESH_HPP
#define SURFACEMESH_HPP

#include <vector>
#include <chrono>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <stdexcept>

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Surface_mesh_simplification/edge_collapse.h>
#include <CGAL/Surface_mesh_simplification/Policies/Edge_collapse/Edge_count_ratio_stop_predicate.h>
#include <CGAL/boost/graph/generators.h>

/*typedef CGAL::Simple_cartesian<double>               Kernel;
typedef Kernel::Point_3                              Point_3;
typedef CGAL::Surface_mesh<Point_3>                  Surface_mesh;
typedef Surface_mesh::Vertex_index vertex_descriptor;*/

using Kernel = CGAL::Simple_cartesian<double>;
using Point_3 = Kernel::Point_3;
using Surface_mesh = CGAL::Surface_mesh<Point_3>;
using vertex_descriptor = Surface_mesh::Vertex_index;
using face_descriptor = Surface_mesh::Face_index;

class SurfaceMesh{
    public:
    SurfaceMesh(std::vector<std::vector<int>> faces, std::vector<std::vector<double>> vertices, double stop_ratio);
    void triangulated_surface_mesh_simplification();
    void updateVerticesCoordinates();
    std::vector<std::vector<double>> getVertices();
    std::vector<std::vector<int>> getFaceIndices();
    void updateFaceIndices();
    std::unordered_map<vertex_descriptor, int> getIndicesRemapping();

    private:
    Surface_mesh m_surface_mesh;
    std::vector<std::vector<int>> m_faces;
    std::vector<std::vector<double>> m_vertices;
    double m_stop_ratio;
};

#endif
