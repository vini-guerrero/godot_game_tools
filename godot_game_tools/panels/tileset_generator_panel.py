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
        box.label(text="Tileset Settings", icon='SCENE')
        box.prop(tool, "tileset_type")
        box.prop(tool, "tileset_generate_path")
        box.prop(tool, "tileset_tile_width")
        box.prop(tool, "tileset_tile_height")
        box.label(text="Camera Shortcuts", icon='CAMERA_DATA')
        # box.operator("wm.tileset_set_topdown_camera", icon="DECORATE_OVERRIDE")
        # box.operator("wm.tileset_set_isometric_camera", icon="CON_TRACKTO")
        box.operator("wm.tileset_move_camera_tile", icon="ANIM_DATA")
        box = layout.box()
        box.label(text="Tile Generation", icon='MATCUBE')
        box.operator("wm.tileset_generate_tile", icon="ADD")
        box.label(text="Collision Settings")
        box.operator("wm.tileset_add_collision_shape", icon="ADD")
        box.operator("wm.tileset_remove_collision_shape", icon="REMOVE")
        box.label(text="Navigation Settings")
        box.operator("wm.tileset_add_navigation_shape", icon="ADD")
        box.operator("wm.tileset_remove_navigation_shape", icon="REMOVE")
        box = layout.box()
        box.label(text="Godot Export", icon='FILEBROWSER')
        box.operator("wm.tileset_export_godot_tileset", icon="EXPORT")
