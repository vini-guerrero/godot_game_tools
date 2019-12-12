import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu)

class _PT_MIXAMO_UTILITIES_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.mixamo_utilities_panel"
    bl_label = "Mixamo Utilies"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    def draw(self, context):
        pass

class _PT_ARMATURE_UTILITIES_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.armature_panel"
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Armature Setup", icon='ARMATURE_DATA')
        # box.prop(tool, "target_name")
        box.operator("wm.init_character", icon="IMPORT")
        box.operator("wm.join_animations", icon="ASSET_MANAGER")
        # box.operator("wm.prepare_mixamo_rig", icon="ASSET_MANAGER")
        box.separator()


class _PT_ROOT_MOTION_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.rootmotion_panel"
    bl_label = "Root Motion"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Root Motion Setup", icon='ANIM_DATA')
        box.prop(tool, "visible_armature")
        box.prop(tool, "rootmotion_all")
        box.operator("wm.add_rootmotion", icon="BONE_DATA")
        box.separator()


class _PT_ANIMATIONS_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.animations_panel"
    bl_label = "Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Animations Settings", icon='SCENE')
        box.prop(tool, "animations")
        box.operator("wm.animation_player", icon="PLAY")
        box.operator("wm.animation_stop", icon="PAUSE")
        box.prop(tool, "action_name")
        box.operator("wm.rename_animation", icon="ARMATURE_DATA")
        box.operator("wm.push_nlas", icon="ANIM_DATA")
        box.separator()
