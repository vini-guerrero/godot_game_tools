import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class GGT_PT_TEXTURE_CONTROLS_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.texture_controls_panel"
    bl_label = "Texture Controls"
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
        box.label(text="Texture Baking", icon='SCENE')
        box.label(text="Work-In-Progress", icon='SORTTIME')
        box.prop(tool, "bake_texture_size")
        box.prop(tool, "bake_texture_name")
        box.operator("wm_ggt.create_bake_texture", icon="FILE_IMAGE")
        # box.prop(tool, "bake_filter")
        box.operator("wm_ggt.bake_texture", icon="ANIM_DATA")
        box.prop(tool, "bake_texture_path")
        box.operator("wm_ggt.save_bake_textures", icon="ANIM_DATA")

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
