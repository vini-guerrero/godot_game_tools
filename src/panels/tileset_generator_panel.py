import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class _PT_TILESET_GENERATOR_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.tileset_utilities_panel"
    bl_label = "Tileset Generator"
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
        box.label(text="Tileset Manager", icon='SCENE')
        box.prop(tool, "tileset_generate_path")
        box.operator("wm.tileset_set_topdown_camera", icon="ANIM_DATA")
        box.operator("wm.tileset_set_isometric_camera", icon="ANIM_DATA")
        box.operator("wm.tileset_generate_tile", icon="ANIM_DATA")
        box.operator("wm.tileset_move_camera_tile", icon="ANIM_DATA")
        box.operator("wm.tileset_export_godot_tileset", icon="ANIM_DATA")
