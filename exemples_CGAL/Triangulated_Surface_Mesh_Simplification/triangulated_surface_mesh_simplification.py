bl_info = {
    "name": "Lindstrom-Turk's 'Triangulated Surface Mesh Simplification' implementation algorithm",
    "author": "Richard Leestmans",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "description": "Script permettant de simplifier le maillage d'un objet en implémentant l'algorithme 'Triangulated Surface Mesh Simplification' de Lindstrom-Turk",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Mesh",
}

import bpy
import bmesh
import mesh_simplification

# On récupère tous les objets présents dans la scène
# objects = bpy.context.scene.objects

def triangulate_mesh(context, mesh):
    if not mesh or mesh.type != 'MESH':
        raise RuntimeError("Aucun maillage n'est sélectionné")
    else:
        if(context.mode == 'OBJECT'):
            bm = bmesh.new()
            bm.from_mesh(mesh.data)
        elif(context.mode == 'EDIT_MESH'):
            bm = bmesh.from_edit_mesh(mesh.data)
        else:
            raise RuntimeError('Vous devez être en mode "Objet" ou en mode "Edition" pour effectuer cette opération.')
            
        # On vérifie que la maillage ne possède pas de doublons en supprimant les sommets qui se superposent
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0001)
        # et on triangule l'ensemble des faces du maillage
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        
        # On met à jour les normales des faces
        bm.normal_update()
        
        # On met à jour le mesh dans le viewport selon le mode dans lequel nous nous situons
        # si nous nous trouvons en mode 'Objet'
        if(context.mode == 'OBJECT'):
            bm.to_mesh(mesh.data)
            bm.free()
        # sinon nous nous trouvons en mode 'Edition'
        else:
            bmesh.update_edit_mesh(mesh.data)
            

def simplify_mesh(context, mesh):
    # On force le maillage à passer en mode objet
    if(context.mode == 'EDIT_MESH'):
        bpy.ops.object.editmode_toggle()
        
    #On applique l'ensemble des transformations effectuées par l'utilisateur sur le maillage
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # Nous commençons par préparer les données à envoyer au code C++ à savoir la liste des indices des sommets par face et les coordonnées des sommets
    # commençons par les indices des sommets des faces
    faces = [face.vertices for face in mesh.data.polygons]
    
    # et pour les coordonnées des sommets du mesh
    vertices = [vertex.co for vertex in mesh.data.vertices]
    
    cgal_mesh = mesh_simplification.SurfaceMesh(faces, vertices, 0.1)
    try:
        cgal_mesh.triangulated_surface_mesh_simplification()
    except Exception as err:
        raise err
    
    cgal_mesh_vertices = cgal_mesh.getVertices()
    print("coordonnées des sommets :")
    print(cgal_mesh_vertices)
    
    cgal_mesh_faces = cgal_mesh.getFaceIndices()
    print("indices des sommets des faces :")
    print(cgal_mesh_faces)
    
    cgal_mesh_edges = []
    
    # on récupère le nom du maillage
    name = mesh.data.name
    
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)    
    
    bpy.ops.object.delete()
     
    # on crée un nouveau maillage dans Blender avec les données récupérées
    new_mesh = bpy.data.meshes.new(name=name)
    new_mesh.from_pydata(cgal_mesh_vertices, cgal_mesh_edges, cgal_mesh_faces)
    # useful for development when the mesh may be invalid.
    new_mesh.update(calc_edges=True)
    new_mesh.validate(verbose=True)
    
    # Créer un objet associé au maillage
    obj = bpy.data.objects.new(name, new_mesh)

    # Ajouter l'objet à la scène
    bpy.context.scene.collection.objects.link(obj)

    # Sélectionner l'objet dans le viewport
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
            

class VIEW3D_OT_mesh_simplification(bpy.types.Operator):
    """Permet de simplifier le maillage d'un objet en appliquant l'algorithme 'Triangulated Surface Mesh Simplification de CGAL"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "view3d.mesh_simplification"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Afficher Informations"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        mesh = context.active_object
        triangulate_mesh(context, mesh)
        simplify_mesh(context, mesh)      
        return {'FINISHED'}


class VIEW3D_PT_mesh_simplification_panel(bpy.types.Panel):

    bl_space_type = "VIEW_3D"  # espace dans lequel est situé le panneau
    bl_region_type = "UI"  # région dans laquelle le panneau se situe

    bl_category = "Mesh Simplification"  # nom du panneau dans la barre latérale
    bl_label = "Mesh Simplification"  # Titre du panneau latéral

    def draw(self, context):
        """define the layout of the panel"""
        row = self.layout.row()
        row.operator("view3d.mesh_simplification", text="Simplifier le maillage")


def register():
    bpy.utils.register_class(VIEW3D_PT_mesh_simplification_panel)
    bpy.utils.register_class(VIEW3D_OT_mesh_simplification)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_mesh_simplification_panel)
    bpy.utils.unregister_class(VIEW3D_OT_mesh_simplification)


if __name__ == "__main__":
    register()