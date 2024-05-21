#include "SurfaceMeshSimplification.hpp"

namespace SMS = CGAL::Surface_mesh_simplification;
namespace py = pybind11;

SurfaceMeshSimplification::SurfaceMeshSimplification(py::dict data) : m_surface_mesh(), m_surface_mesh_data(){
    //On caste toutes les données provenant de notre structure de données python vers des types C++
    const std::vector<int> faces = data["faces"].cast<std::vector<int>>();
    const std::vector<double> vertices = data["vertices"].cast<std::vector<double>>();
    m_stop_ratio = data["decimation_factor"].cast<double>();

    //création d'un tableau de vector_descriptor qui va contenir les informations des coordonnées des sommets du maillage
    std::vector<vertex_descriptor> vertices_descriptor;
    //et réservation de l'espace mémoire adéquat
    vertices_descriptor.reserve(vertices.size() / 3);

    for(int i = 0; i < vertices.size(); i+=3){
        vertex_descriptor v = m_surface_mesh.add_vertex(Point_3(vertices[i], vertices[i+1], vertices[i+2]));
        vertices_descriptor.push_back(v);
    }

    for(int i = 0; i < faces.size(); i+=3){
        //Récupération des indices des sommets de la face courante
        std::vector<int> face_indices(faces.begin() + i, faces.begin() + i + 3);

        //Et création de la face du maillage à partir de ces derniers
        m_surface_mesh.add_face(vertices_descriptor[face_indices[0]], vertices_descriptor[face_indices[1]], vertices_descriptor[face_indices[2]]);
    }
}

void SurfaceMeshSimplification::triangulated_surface_mesh_simplification(){

    if(!CGAL::is_triangle_mesh(m_surface_mesh))
    {
        throw std::runtime_error("Le maillage n'est pas composé que de faces triangulaires...");
    }

    std::chrono::steady_clock::time_point start_time = std::chrono::steady_clock::now();
    // In this example, the simplification stops when the number of undirected edges
    // drops below 10% of the initial count
    SMS::Edge_count_ratio_stop_predicate<Surface_mesh> stop(m_stop_ratio);
    int r = SMS::edge_collapse(m_surface_mesh, stop);
    std::chrono::steady_clock::time_point end_time = std::chrono::steady_clock::now();
    std::cout << "\nFinished!\n" << r << " edges removed.\n" << m_surface_mesh.number_of_edges() << " final edges.\n";
    std::cout << m_surface_mesh.number_of_vertices() << " final vertices.\n";
    std::cout << "Time elapsed: " << std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count() << "ms" << std::endl;

    std::unordered_map<vertex_descriptor, int> remapping = this->get_indices_remapping();

    // Ajout d'une propriété aux faces pour stocker les indices des sommets
    std::pair<Surface_mesh::Property_map<face_descriptor, std::vector<int>>, bool> property = m_surface_mesh.add_property_map<face_descriptor, std::vector<int>>("f:indices");

    Surface_mesh::Property_map<face_descriptor, std::vector<int>> indices_property;
    //Si la propriété existe déjà
    if(!property.second){
        indices_property = m_surface_mesh.property_map<face_descriptor, std::vector<int>>("f:indices").first;
    }else{
        indices_property = property.first;
    }

    // Nous remplissons ensuite la propriété avec les indices des sommets pour chaque face
    // en utilisant les demi-arêtes des faces
    for (const auto& face : m_surface_mesh.faces()) {
        std::vector<int>& indices = indices_property[face];
        
        for (const auto& v : vertices_around_face(m_surface_mesh.halfedge(face), m_surface_mesh)) {
            indices.push_back(remapping[v]);
        }
    }

    this->update_vertices_coordinates();
    this->update_face_indices();
}

void SurfaceMeshSimplification::update_vertices_coordinates(){
    //Création d'un tableau qui va contenir les coordonnées de nos nouveaux résultant de l'algorithme de simplification
    std::vector<double> vertices_coordinates;
    // réservation de l'espace mémoire adéquat
    vertices_coordinates.reserve(num_vertices(m_surface_mesh) * 3);

    //utilisation de propriétés : "location" référence les positions
    const auto& location = m_surface_mesh.property_map<vertex_descriptor, Point_3>("v:point").first;

    for(const auto& vd : m_surface_mesh.vertices()) {
        const std::vector<double> vertex = {location[vd][0], location[vd][1], location[vd][2]};
        std::copy(vertex.begin(), vertex.end(), std::back_inserter(vertices_coordinates));
    }

    //Ajout du tableau dans la structure de données qui sera retournée à Blender
    m_surface_mesh_data["vertices"] = vertices_coordinates;
}

void SurfaceMeshSimplification::update_face_indices(){
    //Création d'un tableau qui va contenir les indices des sommets des faces résultant de l'algorithme de simplification
    std::vector<int> face_indices;
    // et réservation de l'espace mémoire adéquat
    face_indices.reserve(num_faces(m_surface_mesh) * 3);
    const auto& indices_property = m_surface_mesh.property_map<face_descriptor, std::vector<int>>("f:indices").first;

    for(const auto& face : m_surface_mesh.faces()) {
        const std::vector<int>& indices = indices_property[face];
        std::copy(indices.begin(), indices.end(), std::back_inserter(face_indices));
    }
    //Ajout du tableau dans la structure de données qui sera retournée à Blender
    m_surface_mesh_data["faces"] = face_indices;
}

py::dict SurfaceMeshSimplification::get_surface_mesh_data(){
    return m_surface_mesh_data;
}

std::unordered_map<vertex_descriptor, int> SurfaceMeshSimplification::get_indices_remapping(){
    std::unordered_map<vertex_descriptor, int> remapping;

    // Pour ré-indexer le maillage, nous allons parcourir l'ensemble des sommets du maillage
    // et associer pour chacun d'entre eux un indice qui ira de 0 au nombre de sommets du maillage - 1
    int new_index = 0;
    for (const auto& vertex : m_surface_mesh.vertices()) {
        remapping[vertex] = new_index++;
    }

    return remapping;
}

PYBIND11_MODULE(mesh_simplification, handle){
    handle.doc() = "Classe implémentant l'algorithme 'Triangulated Surface Mesh Simplification' de Lindstrom-Turk.";

    py::class_<SurfaceMeshSimplification>(handle, "SurfaceMeshSimplification")
        .def(py::init<py::dict>())
        .def("triangulated_surface_mesh_simplification", &SurfaceMeshSimplification::triangulated_surface_mesh_simplification)
        .def("get_surface_mesh_data", &SurfaceMeshSimplification::get_surface_mesh_data);
}
