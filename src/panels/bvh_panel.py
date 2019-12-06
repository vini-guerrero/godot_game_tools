import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class OBJECT_PT_BVH_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.bvh_utilities_panel"
    bl_label = "BVH Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Work-In-Progress", icon='SCENE')
