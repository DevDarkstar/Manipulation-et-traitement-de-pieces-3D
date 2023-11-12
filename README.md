# Manipulation-et-traitement-de-pieces-3D

Le dépôt contient un dossier << exemples >> dans lequel se trouve divers fichiers permettant de créer un module Python à partir d'un ou de plusieurs fichiers C++.
Pour ce faire, vous devez tout d'abord cloner le dépôt de << Pybind11 >> [Lien](https://github.com/pybind/pybind11) avec :

`git clone https ://github.com/pybind/pybind11.git`

Pybind11 est un module permettant de créer des modules Python à partir de code C++. Veuillez à cloner le dépôt dans le dossier << exemples >>, au même niveau que les fichiers sources.
Vous pouvez ensuite créer votre module Python en générant tout d'abord un Makefile à partir du fichier **CMakeLists.txt** . Il est recommandé de créer un sous-dossier et de générer le Makefile à l'intérieur de ce denier afin de ne pas mélanger les fichiers sources et ceux de compilation.

- Commande pour les systèmes de type Unix : 

`cmake ..`

- Commande pour les systèmes Windows :

`cmake cmake -G "Unix Makefiles" ..`

Puis la commande `make` permet de générer le module Python avec l'extension *.so* pour les systèmes Unix et *.pyd* pour les systèmes Windows. Vous n'avez plus qu'à importer votre module dans votre code Python en utilisant le nom du module qui a été défini dans la macro **PYBIND11_MODULE** du fichier .cpp (premier paramètre).

