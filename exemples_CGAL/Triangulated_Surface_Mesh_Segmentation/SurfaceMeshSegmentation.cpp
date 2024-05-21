#include "SurfaceMeshSegmentation.hpp"

namespace py = pybind11;

SurfaceMeshSegmentation::SurfaceMeshSegmentation(py::dict data) : m_surface_mesh(), m_segments_data(){
    //Toutes les données, provenant de notre structure de données python, sont castées vers leurs types C++ idoines
    const std::vector<double> vertices = data["vertices"].cast<std::vector<double>>();
    const std::vector<int> faces = data["faces"].cast<std::vector<int>>();
    m_clusters = data["clusters"].cast<int>();
    m_smoothness = data["smoothness"].cast<float>();

    //création d'un tableau de vector_descriptor qui va contenir les informations des coordonnées des sommets du maillage
    std::vector<vertex_descriptor> vertices_descriptor;
    //et réservation de l'espace mémoire adéquat
    vertices_descriptor.reserve(vertices.size() / 3);

    for(int i = 0; i < vertices.size(); i+=3){
        const vertex_descriptor& v = m_surface_mesh.add_vertex(Point_3(vertices[i], vertices[i+1], vertices[i+2]));
        vertices_descriptor.push_back(v);
    }

    for(int i = 0; i < faces.size(); i+=3){
        //Récupération des indices des sommets de la face courante
        std::vector<int> face_indices(faces.begin() + i, faces.begin() + i + 3);

        //Et création de la face du maillage à partir de ces derniers
        m_surface_mesh.add_face(vertices_descriptor[face_indices[0]], vertices_descriptor[face_indices[1]], vertices_descriptor[face_indices[2]]);
    }
}

void SurfaceMeshSegmentation::triangulated_surface_mesh_segmentation(){

    if(!CGAL::is_triangle_mesh(m_surface_mesh))
    {
        throw std::runtime_error("Le maillage n'est pas composé que de faces triangulaires...");
    }

    std::chrono::steady_clock::time_point start_time = std::chrono::steady_clock::now();
    Facet_double_map sdf_property_map;
    sdf_property_map = m_surface_mesh.add_property_map<face_descriptor, double>("f:sdf").first;

    // compute SDF values
    // We can't use default parameters for number of rays, and cone angle
    // and the postprocessing
    CGAL::sdf_values(m_surface_mesh, sdf_property_map, 2.0 / 3.0 * CGAL_PI, 25, true);

    // create a property-map for segment-ids
    Facet_int_map segment_property_map = m_surface_mesh.add_property_map<face_descriptor,std::size_t>("f:sid").first;

    // segment the mesh using default parameters for number of levels, and smoothing lambda
    // Any other scalar values can be used instead of using SDF values computed using the CGAL function
    std::size_t number_of_segments = CGAL::segmentation_from_sdf_values(m_surface_mesh, sdf_property_map, segment_property_map, m_clusters, m_smoothness);
    std::chrono::steady_clock::time_point end_time = std::chrono::steady_clock::now();
    std::cout << "Number of segments: " << number_of_segments << std::endl;
    std::cout << "Time elapsed: " << std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count() << "ms" << std::endl;

    m_segments_data["number_of_segments"] = number_of_segments;  

    this->updateSegmentsIds();
}

void SurfaceMeshSegmentation::updateSegmentsIds(){
    //Récupération de la property_map contenant les identifiants des segments obtenus
    const auto segment_property_map = m_surface_mesh.property_map<face_descriptor, std::size_t>("f:sid").first;
    std::vector<size_t> segments_ids;
    segments_ids.reserve(num_faces(m_surface_mesh));

    for(const auto& fd : faces(m_surface_mesh)){
        segments_ids.push_back(segment_property_map[fd]);
    }

    m_segments_data["segments_ids"] = segments_ids;
}

py::dict SurfaceMeshSegmentation::getSegmentsData(){
    return m_segments_data;
}

PYBIND11_MODULE(surface_mesh_segmentation, handle){
    handle.doc() = "Classe implémentant l'algorithme 'Triangulated Surface Mesh Segmentation' de Ilker O. Yaz and Sébastien Loriot.";

    py::class_<SurfaceMeshSegmentation>(handle, "SurfaceMeshSegmentation")
        .def(py::init<py::dict>())
        .def("triangulated_surface_mesh_segmentation", &SurfaceMeshSegmentation::triangulated_surface_mesh_segmentation)
        .def("getSegmentsData", &SurfaceMeshSegmentation::getSegmentsData);
}
