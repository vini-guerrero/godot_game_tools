import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class GGT_PT_BVH_UTILITIES_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.bvh_utilities_panel"
    bl_label = "BVH Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.main_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Work-In-Progress", icon='SORTTIME')

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
