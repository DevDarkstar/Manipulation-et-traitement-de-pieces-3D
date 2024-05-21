bl_info = {
    'name': 'Lindstrom-Turk\'s \'Triangulated Surface Mesh Simplification\' implementation algorithm',
    'author': 'Richard Leestmans',
    'version': (1, 0),
    'blender': (4, 0, 0),
    'description': 'Script permettant de simplifier le maillage d\'un objet en implémentant l\'algorithme \'Triangulated Surface Mesh Simplification\' de Lindstrom-Turk',
    'location': 'VIEW3D > UI > Mesh Simplification',
    'warning': 'Cet algorithme ne fonctionne que sur des maillages connexes!',
    'doc_url': 'https://doc.cgal.org/latest/Surface_mesh_simplification/index.html#Chapter_Triangulated_Surface_Mesh_Simplification',
    'tracker_url': '',
    'category': 'Mesh',
}

import bpy
import bmesh
import numpy as np
from mesh_simplification import SurfaceMeshSimplification

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
            

def simplify_mesh(context, object):
    # Passage du contexte en mode 'OBJET'
    bpy.ops.object.mode_set(mode='OBJECT')
        
    #Nous récupérons toutes les transformations du maillage (translation, rotation, mise à l'échelle)
    translation = object.location
    rotation = object.rotation_euler
    scale = object.scale

    # Récupération du maillage associé à l'objet courant
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
    # et pour les coordonnées des sommets du mesh
    data['vertices'] = vertices

    # Récupération du facteur de décimation contenu dans l'instance de la propriété associée à la scène de Blender
    data['decimation_factor'] = context.scene.simplification_properties.decimation_factor
    
    cgal_mesh = SurfaceMeshSimplification(data)
    try:
        cgal_mesh.triangulated_surface_mesh_simplification()
    except Exception as err:
        raise err
    
    # Récupération de la structure de données du maillage résultant de l'algorithme de décimation réalisé côté C++
    simplified_mesh_data = cgal_mesh.get_surface_mesh_data()
    simplified_mesh_vertices = simplified_mesh_data.get('vertices')
    simplified_mesh_faces = simplified_mesh_data.get('faces')
    
    # Récupération du nom du maillage
    mesh_name = mesh.name
    
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)    
    
    bpy.ops.object.delete()
     
    # on crée un nouveau maillage dans Blender avec les données récupérées
    simplified_mesh = bpy.data.meshes.new(name=mesh_name)
    # new_mesh.from_pydata(cgal_mesh_data.get('vertices'), cgal_mesh_edges, cgal_mesh_data.get('faces'))
    # useful for development when the mesh may be invalid.
    simplified_mesh.vertices.add(len(simplified_mesh_vertices) // 3)
    simplified_mesh.vertices.foreach_set('co', simplified_mesh_vertices)

    total_face_indices = len(simplified_mesh_faces)
    
    simplified_mesh.loops.add(total_face_indices)
    simplified_mesh.loops.foreach_set('vertex_index', simplified_mesh_faces) 
    
    loop_start = range(0, total_face_indices, 3)
    loop_total = [3] * total_face_indices

    simplified_mesh.polygons.add(total_face_indices // 3)
    simplified_mesh.polygons.foreach_set('loop_start', loop_start) 
    simplified_mesh.polygons.foreach_set('loop_total', loop_total)
    simplified_mesh.polygons.foreach_set('use_smooth', [0] * total_face_indices)

    simplified_mesh.update()
    simplified_mesh.validate()
    
    # Création d'un objet Blender auquel associer le maillage
    obj = bpy.data.objects.new(mesh_name, simplified_mesh)

    # Application de l'ensemble des transformations de l'ancien maillage sur le nouveau
    obj.location = translation
    obj.rotation_euler = rotation
    obj.scale = scale

    # Ajout de l'objet à la scène
    bpy.context.scene.collection.objects.link(obj)

    # et sélection de l'objet dans la scène 3D
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
            

class VIEW3D_OT_mesh_simplification(bpy.types.Operator):
    """Permet de simplifier le maillage d'un objet en appliquant l'algorithme 'Triangulated Surface Mesh Simplification de Lindstrom-Turk"""
    bl_idname = 'wm.mesh_simplification'
    bl_label = 'Afficher Informations'     
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        object = context.active_object
        triangulate_mesh(context, object)
        simplify_mesh(context, object)      
        return {'FINISHED'}


class VIEW3D_PT_mesh_simplification_panel(bpy.types.Panel):
    bl_label = 'Mesh Simplification'  # Titre du panneau latéral
    bl_idname = 'VIEW3D_PT_mesh_simplification_panel'
    bl_space_type = 'VIEW_3D'  # espace dans lequel est situé le panneau
    bl_region_type = 'UI'  # région dans laquelle le panneau se situe

    bl_category = 'Mesh Simplification'  # nom du panneau dans la barre latérale

    def draw(self, context):
        # Récupération de l'instance de SimplificationProperties associée à une instance de la classe Scene de Blender
        property = context.scene.simplification_properties
        # Création du contenu de l'onglet de l'extension
        box = self.layout.box()
        box.prop(property, 'decimation_factor')
        row = self.layout.row()
        row.operator(VIEW3D_OT_mesh_simplification.bl_idname, text='Simplifier le maillage')


# classe contenant les propriétés utilisées dans l'algorithme de simplification du maillage
class SimplificationProperties(bpy.types.PropertyGroup):
    # propriété sur le facteur de décimation du maillage (valeur comprise entre 0 et 1)
    decimation_factor: bpy.props.FloatProperty(
        name='facteur décimation',
        description='Facteur de décimation du maillage',
        default=0.5,  # Valeur par défaut
        min=0.0,  # Valeur minimale
        max=1.0,  # Valeur maximale
        step=5,  # Incrémentation pour le curseur (une valeur 'step' de 5 pour une FloatProperty indique un pas de 0.05)
    )


classes = (VIEW3D_PT_mesh_simplification_panel, VIEW3D_OT_mesh_simplification, SimplificationProperties)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.simplification_properties = bpy.props.PointerProperty(type=SimplificationProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.simplification_properties


if __name__ == '__main__':
    register()
