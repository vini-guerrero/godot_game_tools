import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class _PT_TEXTURE_CONTROLS_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.texture_controls_panel"
    bl_label = "Texture Controls"
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
        box.label(text="Texture Baking", icon='SCENE')
        box.label(text="Work-In-Progress", icon='SCENE')
        box.prop(tool, "bake_texture_size")
        box.operator("wm.bake_texture", icon="ANIM_DATA")
        box.operator("wm.save_bake_textures", icon="ANIM_DATA")
