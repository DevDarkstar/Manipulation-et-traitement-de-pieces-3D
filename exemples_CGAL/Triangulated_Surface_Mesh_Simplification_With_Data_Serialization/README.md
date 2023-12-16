# Implémentation de l'algorithme de simplification de maillage de Lindstrom-Turk pour Blender v2

Cet exemple permet d'implémenter l'algorithme de [simplification de maillage de Lindstrom-Turk](https://doc.cgal.org/latest/Surface_mesh_simplification/index.html#Chapter_Triangulated_Surface_Mesh_Simplification) sous la forme d'une **extension** pour Blender en utilisant la sérialisation des données entre Python et C++ via le module Pybind11.

Les fichiers *CMakeLists.txt*, *SurfaceMesh.cpp* et *SurfaceMesh.hpp* permettent de générer le module Python incorporant l'algorithme de simplification de maillage (nécessite [Pybind11](https://github.com/pybind/pybind11) et [CGAL](https://www.cgal.org/) pour générer le module).

Le module Python résultant ainsi que le fichier *triangulated_surface_mesh_simplification.py* doivent être alors ajoutés dans une archive au format *.zip* afin de pouvoir être installée comme extension pour Blender.
