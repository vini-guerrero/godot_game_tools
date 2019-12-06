bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero",
    "version": (1, 0, 3),
    "blender": (2, 81, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "tracker_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "category": "Godot Game Tools"
}

import bpy
import glob
import os
from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.props import (StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)


# ------------------------------------------------------------------------
#    GUI Functions
# ------------------------------------------------------------------------
def populateAnimations(self, context):
    animationsArr = []
    actionNamesList = []
    if len(bpy.data.actions) > 0:
        for action in bpy.data.actions:
            actionNamesList.append(action.name)
        actionNamesList = sorted(actionNamesList)
        for action in actionNamesList:
            item = (action, action, action)
            animationsArr.append(item)
    return animationsArr


def toggleArmatureVisibility(self, context):
    scene = context.scene
    tool = scene.godot_game_tools
    target_armature = tool.target_name
    visible_armature = tool.visible_armature
    bpy.data.objects["Armature"].select_set(True)
    target_armature.hide_viewport = not visible_armature
    bpy.context.object.show_in_front = not visible_armature





# ------------------------------------------------------------------------
#    Addon Scene Properties
# ------------------------------------------------------------------------

class AddonProperties(PropertyGroup):

    action_name: StringProperty(name="New Name", description="Choose the action name you want to rename your animation in the dopesheet", maxlen=1024)
    rootmotion_name: StringProperty(name="Rootmotion Name", description="Choose name you want for the RootMotion Bone", maxlen=1024, default="RootMotion")
    target_name: PointerProperty(name="Target", description="Select the target armature you want the animations to be merged into", type=bpy.types.Object)
    animations: EnumProperty(name="Animations", description="Available armature animations", items=populateAnimations, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    visible_armature: BoolProperty(name="Show Armature Bones", description="Hides / Show armature bones once animations are loaded", default=True, update=toggleArmatureVisibility)
    rootmotion_all: BoolProperty(name="Apply Rootmotion To All Animations", description="Choose to apply rootmotion to all animations or current only", default=True, update=None)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
from operators.nla_tracks_controller import NLA_TRACKS_OT
from operators.animation_controller import ANIMATION_PLAYER_OT, STOP_ANIMATION_OT, RENAME_ANIMATION_OT
from operators.rootmotion_controller import ADD_ROOTBONE_OT, ADD_ROOTMOTION_OT
from operators.mixamo_controller import INIT_CHARACTER_OT, JOIN_ANIMATIONS_OT
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------
#    Panels
# ------------------------------------------------------------------------

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

class OBJECT_PT_MIXAMO_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.mixamo_utilities_panel"
    bl_label = "Mixamo Utilies"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    def draw(self, context):
        pass

class OBJECT_PT_ARMATURE_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.armature_panel"
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
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

class OBJECT_PT_ROOT_MOTION(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.rootmotion_panel"
    bl_label = "Root Motion"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
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

class OBJECT_PT_ANIMATIONS(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.animations_panel"
    bl_label = "Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
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

class OBJECT_PT_ADDON_PANEL(Panel):
    bl_idname = "object.main_panel"
    bl_label = "Godot Game Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Godot Game Tools"
    bl_context = "objectmode"
    def draw(self, context): pass

# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------

classes = (
    AddonProperties,
    OBJECT_PT_ADDON_PANEL,
    OBJECT_PT_MIXAMO_UTILITIES,
    OBJECT_PT_BVH_UTILITIES,
    OBJECT_PT_ARMATURE_UTILITIES,
    OBJECT_PT_ROOT_MOTION,
    OBJECT_PT_ANIMATIONS,
    INIT_CHARACTER_OT,
    JOIN_ANIMATIONS_OT,
    ANIMATION_PLAYER_OT,
    STOP_ANIMATION_OT,
    NLA_TRACKS_OT,
    RENAME_ANIMATION_OT,
    ADD_ROOTBONE_OT,
    ADD_ROOTMOTION_OT
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.godot_game_tools = PointerProperty(type=AddonProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.godot_game_tools

if __name__ == "__main__":
    register()
