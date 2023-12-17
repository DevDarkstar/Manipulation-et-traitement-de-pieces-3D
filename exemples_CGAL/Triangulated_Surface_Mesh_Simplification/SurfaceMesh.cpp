#include "SurfaceMesh.hpp"

namespace SMS = CGAL::Surface_mesh_simplification;
namespace py = pybind11;

SurfaceMesh::SurfaceMesh(std::vector<std::vector<int>> faces, std::vector<std::vector<double>> vertices, double stop_ratio) : m_surface_mesh(), m_faces(), m_vertices(), m_stop_ratio(stop_ratio) {
    //création d'un tableau de vector_descriptor qui va contenir les informations des coordonnées des sommets du maillage
    std::vector<vertex_descriptor> vertices_descriptor;

    for(int i = 0; i < vertices.size(); i++){
        vertex_descriptor v = m_surface_mesh.add_vertex(Point_3(vertices[i][0], vertices[i][1], vertices[i][2]));
        vertices_descriptor.push_back(v);
    }

    for(int i = 0; i < faces.size(); i++){
        //On récupère les indices des sommets de la face
        std::vector<int> face = faces[i];

        //On crée la face du maillage pour à partir des indices des sommets
        m_surface_mesh.add_face(vertices_descriptor[face[0]], vertices_descriptor[face[1]], vertices_descriptor[face[2]]);
    }

    std::cout << "Nombres de sommets : " << num_vertices(m_surface_mesh) << std::endl;
    std::cout << "Nombres d'arêtes : " << num_edges(m_surface_mesh) << std::endl;
    std::cout << "Nombres de faces : " << num_faces(m_surface_mesh) << std::endl;
    std::cout << std::endl;
}

void SurfaceMesh::triangulated_surface_mesh_simplification(){

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

    std::unordered_map<vertex_descriptor, int> remapping = this->getIndicesRemapping();

    // Ajouter une propriété aux faces pour stocker les indices des sommets
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
    for (face_descriptor face : m_surface_mesh.faces()) {
        std::vector<int>& indices = indices_property[face];
        
        for (vertex_descriptor v : vertices_around_face(m_surface_mesh.halfedge(face), m_surface_mesh)) {
            indices.push_back(remapping[v]);
        }
    }

    this->updateVerticesCoordinates();
    this->updateFaceIndices();
}

void SurfaceMesh::updateVerticesCoordinates(){

    //utilisation de propriétés : "location" référence les positions
    //Première méthode pour récupérer cette propriété
    //Surface_mesh::Property_map<vertex_descriptor, Point_3> location = m_surface_mesh.points();
    //Seconde méthode pour récupérer cette propriété
    Surface_mesh::Property_map<vertex_descriptor, Point_3> location = m_surface_mesh.property_map<vertex_descriptor, Point_3>("v:point").first;

    for(vertex_descriptor vd : m_surface_mesh.vertices()) {
        std::vector<double> vertex = {location[vd][0], location[vd][1], location[vd][2]};
        m_vertices.push_back(vertex);
    }
}

void SurfaceMesh::updateFaceIndices(){

    Surface_mesh::Property_map<face_descriptor, std::vector<int>> indices_property = m_surface_mesh.property_map<face_descriptor, std::vector<int>>("f:indices").first;

    for (face_descriptor face : m_surface_mesh.faces()) {
        std::vector<int> indices = indices_property[face];

        m_faces.push_back(indices);

        std::cout << "Face " << face << ": ";
        for (int index : indices) {
            std::cout << index << " ";
        }
        std::cout << std::endl;
    }
}

std::vector<std::vector<double>> SurfaceMesh::getVertices(){
    return m_vertices;
}

std::vector<std::vector<int>> SurfaceMesh::getFaceIndices(){
    return m_faces;
}

std::unordered_map<vertex_descriptor, int> SurfaceMesh::getIndicesRemapping(){
    std::unordered_map<vertex_descriptor, int> remapping;

    // Pour ré-indexer le maillage, nous allons parcourir l'ensemble des sommets du maillage
    // et associer pour chacun d'entre eux un indice qui ira de 0 au nombre de sommets du maillage - 1
    int new_index = 0;
    for (vertex_descriptor vertex : m_surface_mesh.vertices()) {
        remapping[vertex] = new_index++;
    }

    return remapping;
}

PYBIND11_MODULE(mesh_simplification, handle){
    handle.doc() = "Classe implémentant l'algorithme 'Triangulated Surface Mesh Simplification' de CGAL.";

    py::class_<SurfaceMesh>(handle, "SurfaceMesh")
        .def(py::init<std::vector<std::vector<int>>, std::vector<std::vector<double>>, double>())
        .def("triangulated_surface_mesh_simplification", &SurfaceMesh::triangulated_surface_mesh_simplification)
        .def("getVertices", &SurfaceMesh::getVertices)
        .def("getFaceIndices", &SurfaceMesh::getFaceIndices);
}