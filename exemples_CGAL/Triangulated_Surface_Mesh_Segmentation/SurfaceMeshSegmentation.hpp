#ifndef SURFACEMESHSEGMENTATION_HPP
#define SURFACEMESHSEGMENTATION_HPP

#include <vector>
#include <chrono>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <stdexcept>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/mesh_segmentation.h>
#include <CGAL/Polygon_mesh_processing/IO/polygon_mesh_io.h>
#include <CGAL/property_map.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel      Kernel;
typedef Kernel::Point_3                                          Point_3;
typedef CGAL::Surface_mesh<Point_3>                              Surface_mesh;
typedef boost::graph_traits<Surface_mesh>::vertex_descriptor     vertex_descriptor;
typedef boost::graph_traits<Surface_mesh>::face_descriptor       face_descriptor;
typedef Surface_mesh::Property_map<face_descriptor,double>       Facet_double_map;
typedef Surface_mesh::Property_map<face_descriptor, std::size_t> Facet_int_map;

class SurfaceMeshSegmentation{
    public:
    explicit SurfaceMeshSegmentation(pybind11::dict data);
    void triangulated_surface_mesh_segmentation();
    void updateSegmentsIds();
    pybind11::dict getSegmentsData();

    private:
    Surface_mesh m_surface_mesh;
    pybind11::dict m_segments_data;
    int m_clusters;
    float m_smoothness;
};

#endif
