import bpy
import os
from random import random

# On nettoie la console
os.system('cls')

# On récupère tous les objets qui sont sélectionnés dans la scène et qui sont des maillages (meshs)
meshs = [object for object in bpy.context.scene.objects if object.type == 'MESH']

# Si la liste est vide
if not meshs :
    print('Il n\'y a pas de meshs sélectionnés dans la scène.')
# Sinon, on commence par activer l'affichage des couleurs des différents meshs dans le mode de rendu solid
else :
    for area in bpy.context.screen.areas: 
        if area.type == 'VIEW_3D':
            for space in area.spaces: 
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.color_type = 'OBJECT' 
    # Puis on attribue une couleur aléatoire à chaque meshs dans la scène
    for mesh in meshs :
        mesh.color = (random(), random(), random(), 1)
