import bpy
import json
import ast

from bpy.props import (StringProperty, FloatProperty, PointerProperty, CollectionProperty)
from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.types import (Panel, Menu, UIList)

class GGT_PT_CHARACTER_UTILITIES_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.character_utilities_panel"
    bl_label = "Character Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.main_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context): pass

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_PT_ARMATURE_UTILITIES_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.armature_panel"
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.character_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Armature Setup", icon='ARMATURE_DATA')
        box.prop(tool, "hips_scale")
        box.operator("wm_ggt.init_character", icon="IMPORT")
        box.operator("wm_ggt.join_animations", icon="ASSET_MANAGER")
        if tool.target_object: box.operator("wm_ggt.armature_join_mesh", icon="GROUP_BONE")
        # if tool.target_object: box.prop(tool, "target_object")
        box.separator()

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_PT_ROOT_MOTION_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.rootmotion_panel"
    bl_label = "Root Motion"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.character_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        ob = tool.target_object
        box = layout.box()
        box.label(text="Root Motion Setup", icon='ANIM_DATA')
        rootmotionRow = box.row()
        rootmotionRow.prop(tool, "visible_armature")
        rootmotionRow.prop(tool, "rootmotion_all")
        rootmotionRow2 = box.row()
        rootmotionRow2.prop(tool, "rootmotion_animation_air_fix")
        rootmotionRow2.prop(tool, "rootMotion_start_frame")
        rootmotionRow3 = box.row()
        rootmotionRow3.prop(tool, "motion_axis")
        rootmotionRow4 = box.row()
        rootmotionRow4.prop(tool, "rootmotion_name")
        rootmotionRow5 = box.row()
        rootmotionRow5.prop_search(tool, "rootmotion_hip_bone", ob.data, "bones", text="Root Bone")
        if ob is not None and tool.rootmotion_hip_bone:
            # box.prop(ob.animation_data.action.ggt_props, "use_root_motion")
            # box.prop(ob.animation_data.action.ggt_props, "use_root_motion_z")
            # box.operator("wm_ggt.add_rootmotion", icon="BONE_DATA")
            # box.operator("wm_ggt.add_rootmotion_legacy", icon="BONE_DATA")
            box.operator("wm_ggt.add_rootmotion_toggle", icon="BONE_DATA")
        box.separator()

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class ACTION_UL_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = "ANIM_DATA"
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            pass

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_PT_ANIMATIONS_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.animations_panel"
    bl_label = "Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.character_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool = scene.godot_game_tools
        ob = tool.target_object
        layout.template_list("ACTION_UL_list", "", bpy.data, "actions", scene, "action_list_index")
        box = layout.box()
        box.operator("wm_ggt.animation_player", icon="PLAY")
        box.operator("wm_ggt.animation_stop", icon="PAUSE")
        box.operator("wm_ggt.delete_animation", icon="TRASH")

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_PT_ANIMATION_UTILITIES_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.animation_utilities"
    bl_label = "Trim Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.animations_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        trimAnimationBox = layout.box()
        trimAnimationBox.label(text="Trim Animations", icon='DOCUMENTS')
        trimAnimationBox.prop(tool, "trim_animation_name")
        trimAnimationRow = trimAnimationBox.row()
        trimAnimationRow.prop(tool, "trim_animation_from")
        trimAnimationRow.prop(tool, "trim_animation_to")
        trimAnimationBox.operator("wm_ggt.trim_animation", icon="SELECT_SET")

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_PT_EXPORT_CHARACTER_PT_GGT(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "obj_ggt.export_character_panel"
    bl_label = "Export Character"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "obj_ggt.character_utilities_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        if target_armature:
            box = layout.box()
            box.prop(tool, "character_export_character_name")
            box.prop(tool, "character_export_path")
            box.prop(tool, "character_export_format")
            animationRow = box.row()
            animationRow.prop(tool, "character_export_animation_loops")
            animationRow.prop(tool, "character_export_create_animation_tree")
            if tool.character_export_create_animation_tree:
                box.operator("wm_ggt.load_animation_tree_preset", icon="EXPORT")
                if target_armature["animation_tree_preset"]:
                    animation_tree_preset = ast.literal_eval(target_armature["animation_tree_preset"])
                    animations = animation_tree_preset["animations"]
                    for animation in animations.keys():
                        box.prop_search(target_armature, '["' + animation + '"]', bpy.data, "actions", text=animation)
            if tool.character_export_path:
                box.operator("wm_ggt.character_export", icon="EXPORT")

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
