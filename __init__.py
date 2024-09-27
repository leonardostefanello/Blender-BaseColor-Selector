# -------------------- IMPORTS --------------------

import bpy

# -------------------- INFORMATION --------------------

bl_info = {
    "name": "BaseColor Selector",
    "author": "Moonlight_",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "category": "Object",
    "location": "3D Viewport > Sidebar > BaseColor Selector",
    "description": "Selects all objects with the same Base Color.",
    "doc_url": "github.com/leonardostefanello/Blender-BaseColor-Selector/blob/main/README.md",
    "tracker_url": "github.com/leonardostefanello/Blender-BaseColor-Selector/issues",
}

# -------------------- UI PANEL SETUP --------------------

class OBJECT_PT_MatchBaseColorPanel(bpy.types.Panel):
    bl_label = "Match Base Color"
    bl_idname = "OBJECT_PT_match_base_color_panel"  # Unique identifier for the panel
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BaseColor Selector'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Display the count of objects with the same base color as text
        layout.label(text=f"Objects with same color: {scene.matched_object_count}")
        
        # Button to execute the base color matching operation
        layout.operator("object.match_base_color", text="Match Base Color")
        
        # Button to clean duplicate materials from the selected object
        layout.operator("object.clean_materials", text="Clean Materials")

# -------------------- OPERATOR FOR MATCHING BASE COLOR --------------------

class OBJECT_OT_MatchBaseColor(bpy.types.Operator):
    bl_label = "Match Base Color"  # Label for the operator
    bl_idname = "object.match_base_color"  # Unique identifier for the operator
    
    @staticmethod
    def get_base_color(material):
        # Function to retrieve the base color from a material
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    return node.inputs['Base Color'].default_value
        return None  # Return None if no base color is found
    
    def execute(self, context):
        obj = context.active_object  # Get the currently active object
        
        # Check if the active object has a material
        if obj and obj.active_material:
            base_color = self.get_base_color(obj.active_material)  # Get the base color of the active object's material
            
            if base_color is None:
                self.report({'WARNING'}, "Selected object has no Principled BSDF with Base Color.")
                return {'CANCELLED'}  # Exit if no base color is found
            
            matched_objects = []  # List to store matched objects
            
            # Iterate through all objects in the scene
            for other_obj in bpy.context.scene.objects:
                if other_obj.type == 'MESH' and other_obj.active_material:
                    other_color = self.get_base_color(other_obj.active_material)  # Get the base color of the other object's material
                    # Check if the colors are similar within a small threshold
                    if other_color and all(abs(base_color[i] - other_color[i]) < 0.001 for i in range(3)):
                        matched_objects.append(other_obj)  # Add matched objects to the list
                        other_obj.select_set(True)  # Select the matched object
            
            context.scene.matched_object_count = len(matched_objects)  # Update the count of matched objects
        else:
            self.report({'WARNING'}, "No active object with material selected.")
            return {'CANCELLED'}  # Exit if no valid object is found
        
        return {'FINISHED'}  # Indicate that the operation was successful

# -------------------- OPERATOR FOR CLEANING MATERIALS --------------------

class OBJECT_OT_CleanMaterials(bpy.types.Operator):
    bl_label = "Clean Materials"  # Label for the operator
    bl_idname = "object.clean_materials"  # Unique identifier for the operator

    def execute(self, context):
        obj = context.active_object  # Get the currently active object

        # Check if the active object is a mesh
        if obj and obj.type == 'MESH':
            # Check if the object has any material slots
            if obj.material_slots:
                material = obj.material_slots[0].material  # Get the first material from the slots
                # Clear all other materials, keeping only the first one
                obj.data.materials.clear()
                obj.data.materials.append(material)
                self.report({'INFO'}, "Removed duplicate materials and kept the first one.")
            else:
                self.report({'WARNING'}, "Object has no materials.")
        else:
            self.report({'WARNING'}, "No mesh object selected.")
        
        return {'FINISHED'}  # Indicate that the operation was successful

# -------------------- REGISTER FUNCTIONS --------------------

def register():
    bpy.utils.register_class(OBJECT_PT_MatchBaseColorPanel)  # Register the panel class
    bpy.utils.register_class(OBJECT_OT_MatchBaseColor)  # Register the base color matching operator
    bpy.utils.register_class(OBJECT_OT_CleanMaterials)  # Register the clean materials operator
    
    # Define a property to hold the count of matched objects
    bpy.types.Scene.matched_object_count = bpy.props.IntProperty(name="Matched Objects", default=0)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_MatchBaseColorPanel)  # Unregister the panel class
    bpy.utils.unregister_class(OBJECT_OT_MatchBaseColor)  # Unregister the base color matching operator
    bpy.utils.unregister_class(OBJECT_OT_CleanMaterials)  # Unregister the clean materials operator
    
    del bpy.types.Scene.matched_object_count  # Remove the matched objects property

# -------------------- ENTRY POINT --------------------

if __name__ == "__main__":
    register()

# -------------------- END --------------------
