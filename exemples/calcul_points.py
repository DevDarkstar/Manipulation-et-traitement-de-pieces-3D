bl_info = {
    "name": "Calcul points",
    "author": "Richard Leestmans",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "SpaceBar Search -> Add-on Preferences Example",
    "description": "Exemple Add-on",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Mesh",
}

import bpy
import count_objects

# On récupère tous les objets présents dans la scène
# objects = bpy.context.scene.objects

class Globals:   
    selected_objects = 0
    vertices_number = 0
    faces_number = 0


def display_infos(context):
    # On récupère tous les objets qui sont sélectionnés dans la scène et qui sont des maillages (meshs)
    selected_meshs = [object for object in bpy.context.selected_objects if object.type == 'MESH']

    # Si la liste est vide
    if not selected_meshs :
        print('Il n\'y a pas de meshs sélectionnés dans la scène.')
        Globals.selected_objects = 0
        Globals.vertices_number = 0
        Globals.faces_number = 0
    # Sinon on compte le nombre de sommets de chaque meshs et on fait le total
    else :
        Globals.selected_objects = len(selected_meshs)
        print('Il y a {} meshs sélectionnés :'.format(len(selected_meshs)))
        total_vertices = 0
        total_faces = 0
        for mesh in selected_meshs :
            vertices_list = []
            for vertice in mesh.data.vertices:
                vertices_list.append(vertice.co)
            # On récupère le nombre de sommets du mesh
            vertices = count_objects.getVerticesNumber(vertices_list)
            print('Un mesh appelé {} et possédant {} sommets;'.format(mesh.name, vertices))
            total_vertices += vertices
            
            faces_list = []
            for face in mesh.data.polygons:
                faces_list.append(face.vertices)
            # On récupère le nombre de sommets du mesh
            faces = count_objects.getFacesNumber(faces_list)
            print('Ainsi que {} faces;'.format(faces))
            total_faces += faces
            # afficher les coordonnées des sommets
            # for vertice in mesh.data.vertices:
            #    print(vertice.co)
        print('Au total, l\'ensemble des meshs sélectionnés représentent {} sommets.'.format(total_vertices))
        Globals.vertices_number = total_vertices
        Globals.faces_number = total_faces
        
def test_divide_by_zero(context):
    try:
        count_objects.testDivideByNumber(0.0)
    except RuntimeError as err:
        raise err


class VIEW3D_OT_count_object(bpy.types.Operator):
    """Permet de compter des informations dans la scène"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "view3d.count_object"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Afficher Informations"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        display_infos(context)      
        return {'FINISHED'}
    
class VIEW3D_OT_test_division(bpy.types.Operator):
    """Permet de tester si une division par zéro existe"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "view3d.test_division"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Test division par zéro"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        test_divide_by_zero(context)      
        return {'FINISHED'}


class VIEW3D_PT_test_panel(bpy.types.Panel):

    bl_space_type = "VIEW_3D"  # espace dans lequel est situé le panneau
    bl_region_type = "UI"  # région dans laquelle le panneau se situe

    bl_category = "test"  # nom du panneau dans la barre latérale
    bl_label = "Mon panneau test"  # Titre du panneau latéral

    def draw(self, context):
        """define the layout of the panel"""
        row = self.layout.row()
        row.operator("view3d.count_object", text="Afficher informations")
        row = self.layout.row()
        row.operator("view3d.test_division", text="Test division par zéro")
        row = self.layout.row()
        row.label(text="Nombre d'objets sélectionnés : {}".format(Globals.selected_objects))
        row = self.layout.row()
        row.label(text="Nombre total de sommets : {}".format(Globals.vertices_number))
        row = self.layout.row()
        row.label(text="Nombre total de faces : {}".format(Globals.faces_number))


def register():
    bpy.utils.register_class(VIEW3D_PT_test_panel)
    bpy.utils.register_class(VIEW3D_OT_count_object)
    bpy.utils.register_class(VIEW3D_OT_test_division)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_test_panel)
    bpy.utils.unregister_class(VIEW3D_OT_count_object)
    bpy.utils.unregister_class(VIEW3D_OT_test_division)


if __name__ == "__main__":
    register()
