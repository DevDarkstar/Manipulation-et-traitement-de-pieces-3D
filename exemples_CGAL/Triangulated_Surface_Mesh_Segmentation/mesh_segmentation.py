bl_info = {
    'name': 'Ilker O. Yaz and Sébastien Loriot \'Triangulated Surface Mesh Segmentation\' implementation algorithm',
    'author': 'Richard Leestmans',
    'version': (2, 0),
    'blender': (4, 0, 0),
    'location': 'VIEW3D > UI > Segmentation',
    'description': 'Implémentation de l\'algorithme de Segmentation (décomposition d\'un maillage en sous-maillages plus petits et significatifs) utilisant la \'function Shape Diameter\' (SDF) pour Blender.',
    'doc_url': 'https://doc.cgal.org/latest/Surface_mesh_segmentation/index.html#Chapter_3D_SurfaceSegmentation',
    'tracker_url': '',
    'category': 'Mesh',
}

import bpy
import bmesh
import numpy as np
import random
from surface_mesh_segmentation import SurfaceMeshSegmentation

# Permet de trianguler un maillage en fonction du contexte utilisé
def triangulate_mesh(context, object):
    if not object or object.type != 'MESH':
        raise RuntimeError('Aucun maillage n\'est sélectionné')
    else:
        mesh = object.data
        # Si nous nous situons en mode 'Objet'
        if(context.mode == 'OBJECT'):
            bm = bmesh.new()
            bm.from_mesh(mesh)
        # Sinon si nous nous situons en mode 'Edition'
        elif(context.mode == 'EDIT_MESH'):
            bm = bmesh.from_edit_mesh(mesh)
        # Sinon nous ne nous situons ni en mode 'Objet' ni en mode 'Edition'
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
            
        # On vérifie que la maillage ne possède pas de doublons en supprimant les sommets qui se superposent
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
        # et on triangule l'ensemble des faces du maillage
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        
        # On met à jour le mesh dans le viewport selon le mode dans lequel nous nous situons
        # si nous nous trouvons en mode 'Objet'
        if(context.mode == 'OBJECT'):
            bm.to_mesh(mesh)
            bm.free()
        # sinon nous nous trouvons en mode 'Edition'
        else:
            bmesh.update_edit_mesh(mesh)


def mesh_segmentation(context, object):
    # Récupération du maillage de l'objet courant
    mesh = object.data  
    # Nous commençons par préparer les données à envoyer au code C++ à savoir la liste des indices des sommets par face et les coordonnées des sommets ainsi que le facteur de décimation de l'algorithme
    # Nous créons pour cela une structure de données sous la forme d'un dictionnaire python
    data = {}
    # commençons par les indices des sommets des faces
    faces = np.zeros((len(mesh.polygons) * 3), dtype=np.int32)
    mesh.polygons.foreach_get('vertices', faces)
    data['faces'] = faces
    
    vertices = np.zeros((len(mesh.vertices) * 3), dtype=np.float32)
    mesh.vertices.foreach_get('co', vertices)
    # et pour les coordonnées des sommets du maillage
    data['vertices'] = vertices

    # Nous récupérons ensuite les deux propriétés de l'algorithme 'clusters' et 'smoothness'
    properties = context.scene.segmentation_properties
    data['clusters'] = properties.clusters
    data['smoothness'] = properties.smoothness
    
    cgal_mesh = SurfaceMeshSegmentation(data)
    try:
        cgal_mesh.triangulated_surface_mesh_segmentation()
    except Exception as err:
        raise err
    
    # Récupération des données issues de la segmentation du maillage
    segments_data = cgal_mesh.getSegmentsData()
    
    # Récupération du tableau des identifiants des segments obtenus
    segments_ids = segments_data.get('segments_ids')
    # Récupération du nombre de segments obtenus
    nb_segments = segments_data.get('number_of_segments')

    # Vérification si l'utilisateur a souhaité supprimer les matériaux déjà associés au maillage
    if properties.delete_materials:
        mesh.materials.clear()

    #Récupération du nombre de matériaux déjà associés au maillage (servira d'offset pour affecter le bon matériau à la bonne face)
    nb_materials = len(mesh.materials)

    # Création des matériaux en fonction du nombre de segments
    for _ in range(nb_segments):
        # Création d'une couleur aléatoire
        red = random.random()
        green = random.random()
        blue = random.random()

        color = (red, green, blue, 1.0)

        material = bpy.data.materials.new(name="Material")

        # Définition de la couleur du matériau
        material.diffuse_color = color

        # affectation du nouveau matériau au maillage
        mesh.materials.append(material)
    
    # Parcours des faces du maillage et affectation du matériau correspondant à l'indice du segment obtenu
    for face, id in zip(mesh.polygons, segments_ids):
        face.material_index = id + nb_materials


# classe contenant les propriétés utilisées dans l'algorithme de segmentation
class SegmentationProperties(bpy.types.PropertyGroup):
    # propriété sur le nombre de clusters à utiliser dans l'algorithme
    clusters: bpy.props.IntProperty(
        name='clusters',
        description='Nombre de clusters de l\'algorithme de segmentation',
        default=4,  # Valeur par défaut
        min=2,  # Valeur minimale
        max=10,  # Valeur maximale
        step=1,  # Incrémentation pour le curseur
    )
    # propriété sur la finesse de la segmenation (plus la valeur est élevée, plus le nombre de segments résultants le sera également)
    smoothness: bpy.props.FloatProperty(
        name='finesse',
        description='Finesse de la segmentation',
        default=0.5,  # Valeur par défaut
        min=0.0,  # Valeur minimale
        max=1.0,  # Valeur maximale
        step=5,  # Incrémentation pour le curseur (une valeur 'step' de 5 pour une FloatProperty indique un pas de 0.05)
    )
    #propriété permettant de demander à l'utilisateur s'il souhaite supprimer les matériaux déjà associés au maillage
    delete_materials: bpy.props.BoolProperty(
        name='suppression matériaux ?',
        description='Suppression des matériaux déjà associés au maillage',
        default=False
    )


class VIEW3D_OT_segment_mesh(bpy.types.Operator):
    bl_idname = 'wm.segment_mesh'
    bl_label = 'Exécution de l\'algorithme de segmentation'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # récupération de l'objet actif dans la scène
        object = context.active_object
        triangulate_mesh(context, object)
        mesh_segmentation(context, object)
        return {'FINISHED'}


class VIEW3D_PT_segmentation_panel(bpy.types.Panel):
    bl_label = 'Segmentation d\'un maillage triangulé'  # Titre du panneau latéral
    bl_idname = 'VIEW3D_PT_segmentation_panel'
    bl_space_type = 'VIEW_3D'  # espace dans lequel est situé le panneau
    bl_region_type = 'UI'  # région dans laquelle le panneau se situe

    bl_category = 'Segmentation'  # nom du panneau dans la barre latérale

    def draw(self, context):
        # nous récupérons l'instance de la classe SegmentationProperties
        properties = context.scene.segmentation_properties
        # nous créons un layout de type 'box' dans lequel nous allons afficher nos propriétés sous la forme de curseurs
        box = self.layout.box()
        box.prop(properties, 'clusters')
        box.prop(properties, 'smoothness')
        box.prop(properties, 'delete_materials')
        # création d'une nouvelle ligne dans laquelle nous ajoutons un bouton (instance de la classe VIEW3D_OT_segmentation_button)
        row = self.layout.row()
        # l'opérateur est référencé par un nom correspondant à la valeur de l'attribut bl_idname de la classe
        row.operator(VIEW3D_OT_segment_mesh.bl_idname, text='Segmenter le maillage')


# tuple contenant les classes à enregistrer et désinscrire dans Blender
classes = (VIEW3D_PT_segmentation_panel, VIEW3D_OT_segment_mesh, SegmentationProperties)
        

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # ajout de la strcture de données de propriétés à la classe Scene de bpy.types via un pointeur de propriété appelé ici segmentation_properties
    # Cela permet d'utiliser une instance de SegmentationProperties dans l'ensemble des classes du script (via bpy.context.scene.segmentation_properties)
    bpy.types.Scene.segmentation_properties = bpy.props.PointerProperty(type=SegmentationProperties)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.segmentation_properties
    
if __name__ == '__main__':
    register()
