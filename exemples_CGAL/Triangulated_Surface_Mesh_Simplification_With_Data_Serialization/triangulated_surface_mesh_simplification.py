bl_info = {
    "name": "Lindstrom-Turk's 'Triangulated Surface Mesh Simplification' implementation algorithm",
    "author": "Richard Leestmans",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "description": "Script permettant de simplifier le maillage d'un objet en implémentant l'algorithme 'Triangulated Surface Mesh Simplification' de Lindstrom-Turk",
    "warning": "Cet algorithme ne fonctionne que sur des maillages connexes! Pour vérifier que votre maillage est connexe du point de vue de Blender, vous pouvez passer en mode 'édition', et passez en mode de sélection 'faces'. Puis appuyez sur la touche 'L' tout en ayant le curseur de votre souris sur votre maillage. Si tout le maillage est sélectionné, alors il est considéré comme connexe.",
    "doc_url": "https://doc.cgal.org/latest/Surface_mesh_simplification/index.html#Chapter_Triangulated_Surface_Mesh_Simplification",
    "tracker_url": "",
    "category": "Mesh",
}

import bpy
import bmesh
from mesh_simplification import SurfaceMesh

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
    
    # Nous commençons par préparer les données à envoyer au code C++ à savoir la liste des indices des sommets par face et les coordonnées des sommets ainsi que le facteur de décimation de l'algorithme
    # Nous créons pour cela une structure de données sous la forme d'un dictionnaire python
    data = {}
    # commençons par les indices des sommets des faces
    data["faces"] = [face.vertices for face in mesh.data.polygons]
    
    # et pour les coordonnées des sommets du mesh
    data["vertices"] = [vertex.co for vertex in mesh.data.vertices]

    # ainsi que pour le facteur de décimation
    data["decimation_factor"] = 0.1
    
    cgal_mesh = SurfaceMesh(data)
    try:
        cgal_mesh.triangulated_surface_mesh_simplification()
    except Exception as err:
        raise err
    
    # On récupère la structure de données du maillage résultant de l'algorithme de décimation réalisé côté C++
    cgal_mesh_data = cgal_mesh.getSurfaceMeshData()
    
    cgal_mesh_edges = []
    
    # on récupère le nom du maillage
    name = mesh.data.name
    
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)    
    
    bpy.ops.object.delete()
     
    # on crée un nouveau maillage dans Blender avec les données récupérées
    new_mesh = bpy.data.meshes.new(name=name)
    new_mesh.from_pydata(cgal_mesh_data.get("vertices"), cgal_mesh_edges, cgal_mesh_data.get("faces"))
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
    """Permet de simplifier le maillage d'un objet en appliquant l'algorithme 'Triangulated Surface Mesh Simplification de Lindstrom-Turk"""      # Use this as a tooltip for menu items and buttons.
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


classes = (VIEW3D_PT_mesh_simplification_panel, VIEW3D_OT_mesh_simplification)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
