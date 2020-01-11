import bpy

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu, UIList)

class _PT_MIXAMO_UTILITIES_PT_(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.mixamo_utilities_panel"
    bl_label = "Mixamo Utilies"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    bl_options = {"DEFAULT_CLOSED"}
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
        ob = tool.target_object
        box = layout.box()
        box.label(text="Root Motion Setup", icon='ANIM_DATA')
        box.prop(tool, "visible_armature")
        box.prop(tool, "rootmotion_all")
        if ob is not None:
            box.prop(ob.animation_data.action.ggt_props, "use_root_motion")
            box.prop(ob.animation_data.action.ggt_props, "use_root_motion_z")
        box.operator("wm.add_rootmotion", icon="BONE_DATA")
        box.separator()

class ACTION_UL_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = "ANIM_DATA"
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            pass

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
        tool = scene.godot_game_tools
        ob = tool.target_object
        layout.template_list("ACTION_UL_list", "", bpy.data, "actions", scene, "action_list_index")
        box = layout.box()
        box.operator("wm.animation_player", icon="PLAY")
        box.operator("wm.animation_stop", icon="PAUSE")
        # box.prop(tool, "action_name")
        # box.operator("wm.rename_animation", icon="ARMATURE_DATA")
        box.operator("wm.push_nlas", icon="ANIM_DATA")
        box.separator()
