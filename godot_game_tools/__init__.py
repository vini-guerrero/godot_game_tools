import bpy
import glob
import os

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.props import (IntProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty, FloatProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)

bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero",
    "version": (2, 0, 0),
    "blender": (2, 82, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "tracker_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "category": "Godot Game Tools"
}

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
    target_armature = tool.target_object
    visible_armature = tool.visible_armature
    bpy.data.objects["Armature"].select_set(True)
    target_armature.hide_viewport = not visible_armature
    bpy.context.object.show_in_front = not visible_armature

def updateTilesetGeneratorCamera(self, context):
    scene = context.scene
    tool = scene.godot_game_tools
    if int(tool.tileset_type) == 0:
        bpy.ops.wm_ggt.tileset_set_topdown_camera('EXEC_DEFAULT')
    elif int(tool.tileset_type) == 1:
        bpy.ops.wm_ggt.tileset_set_isometric_camera('EXEC_DEFAULT')

def update_action_list(self, context):
    ob = context.scene.godot_game_tools.target_object
    if ob is None: return
    ob.animation_data.action = bpy.data.actions[context.scene.action_list_index]
    bpy.context.scene.frame_current = 1
    bpy.context.scene.frame_end = ob.animation_data.action.frame_range[1]

def toggle_use_root_motion(self, context):
    bpy.ops.wm_ggt.animation_stop('EXEC_DEFAULT')
    bpy.ops.wm_ggt.update_rootmotion('EXEC_DEFAULT')

def toggle_use_root_motion_z(self, context):
    bpy.ops.wm_ggt.animation_stop('EXEC_DEFAULT')
    bpy.ops.wm_ggt.update_rootmotion('EXEC_DEFAULT')

# ------------------------------------------------------------------------
#    Addon Tool Properties
# ------------------------------------------------------------------------
class AddonProperties(PropertyGroup):
    action_name: StringProperty(name="New Name", description="Choose the action name you want to rename your animation in the dopesheet", maxlen=1024)
    rootmotion_name: StringProperty(name="Rootmotion Name", description="Choose name you want for the RootMotion Bone", maxlen=1024, default="RootMotion")
    target_object: PointerProperty(name="Target", description="Select the target armature you want the animations to be merged into", type=bpy.types.Object)
    animations: EnumProperty(name="Animations", description="Available armature animations", items=populateAnimations, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    visible_armature: BoolProperty(name="Show Armature Bones", description="Hides / Show armature bones once animations are loaded", default=True, update=toggleArmatureVisibility)
    rootmotion_all: BoolProperty(name="Apply Rootmotion To All Animations", description="Choose to apply rootmotion to all animations or current only", default=True, update=None)
    bake_texture_size: IntProperty(name="Bake Texture Size", description="Define here the size of textures images to bake", default = 1024, min = 8, max = 4096)
    bake_texture_name: StringProperty(name="Bake Name", description="Select the texture name to be saved", maxlen=1024)
    bake_texture_path: StringProperty(name="Texture Path", description="Select the path destination folder you want textures to be saved", subtype="FILE_PATH")
    bake_filter: EnumProperty(name="Bake Map", description="Choose between available bake maps", items=[('GLOSSY', "GLOSSY", ""),('DIFFUSE', "DIFFUSE", "")], update=None, get=None, set=None)
    character_collection_name: bpy.props.StringProperty(name="Armature Collection Name", default="CharacterCollection")
    tile_collection_name: bpy.props.StringProperty(name="Tile Collection Name", default="TileCollection")
    tileset_generate_path: StringProperty(name="Tileset Path", description="Select the path destination folder where you want tileset to be exported", subtype="FILE_PATH")
    tileset_tile_width: IntProperty(name="Tile Width", description="Define the desired tiles width", default=32, min=8, max=1024, update=updateTilesetGeneratorCamera, get=None, set=None)
    tileset_tile_height: IntProperty(name="Tile Height", description="Define the desired tiles height", default=32, min=8, max=1024, update=updateTilesetGeneratorCamera, get=None, set=None)
    tileset_type: EnumProperty(name="Tileset Type", description="Choose between available tileset types", items=[('0', "Top-Down", ""),('1', "Isometric", "")], update=updateTilesetGeneratorCamera, get=None, set=None)
    actions = []

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

# ------------------------------------------------------------------------
#    Action Properties
# ------------------------------------------------------------------------
class ActionProperties(bpy.types.PropertyGroup):
    hips_scale: FloatProperty(name="Hips Scale", description="Hips scale factor", default=1.0)
    use_root_motion: BoolProperty(name="Root Motion", description="Should this animation use root motion", options={'ANIMATABLE'}, default=True, update=toggle_use_root_motion)
    use_root_motion_z: BoolProperty(name="Root Motion Z", description="Use z-axis with this animation", default=False, update=toggle_use_root_motion_z)

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
from .operators.nla_tracks_controller import (
    NLA_TRACKS_OT
)
from .operators.animation_controller import (
    ANIMATION_PLAYER_OT,
    STOP_ANIMATION_OT,
    RENAME_ANIMATION_OT,
    PROCESS_ACTIONS_OT
)
from .operators.rootmotion_controller import (
    ADD_ROOTBONE_OT,
    ADD_ROOTMOTION_OT,
    UPDATE_ROOTMOTION_OT
)
from .operators.mixamo_controller import (
    INIT_CHARACTER_OT,
    JOIN_ANIMATIONS_OT,
    PREPARE_RIG_OT,
    RENAME_RIG_OT
)
from .operators.texture_controller import (
    SAVE_BAKE_TEXTURES_OT,
    CREATE_BAKE_TEXTURES_OT,
    BAKE_TEXTURE_OT
)
from .operators.tileset_controller import (
    TILESET_GENERATE_TILE_OT,
    TILESET_SET_ISOMETRIC_CAMERA_OT,
    TILESET_MOVE_CAMERA_TILE_OT,
    TILESET_SET_TOPDOWN_CAMERA_OT,
    TILESET_EXPORT_GODOT_TILESET_OT,
    TILESET_ADD_COLLISION_SHAPE_OT,
    TILESET_REMOVE_COLLISION_SHAPE_OT,
    TILESET_ADD_NAVIGATION_SHAPE_OT,
    TILESET_REMOVE_NAVIGATION_SHAPE_OT,
    TILESET_ADD_RENDER_SETUP_OT
)
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------
#    Panels
# ------------------------------------------------------------------------
from .panels.bvh_utilities_panel import (GGT_PT_BVH_UTILITIES_PT_GGT)
from .panels.texture_controls_panel import (GGT_PT_TEXTURE_CONTROLS_PT_GGT)
from .panels.mixamo_utilities_panel import (GGT_PT_MIXAMO_UTILITIES_PT_GGT, GGT_PT_ARMATURE_UTILITIES_PT_GGT, ACTION_UL_list, GGT_PT_ROOT_MOTION_PT_GGT, GGT_PT_ANIMATIONS_PT_GGT)
from .panels.tileset_generator_panel import (GGT_PT_TILESET_GENERATOR_PT_GGT)
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------
#    MAIN ADD-ON PANEL
# ------------------------------------------------------------------------
class GGT_PT_MAINPANEL_PT_(Panel):
    bl_idname = "obj_ggt.main_panel"
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
    ActionProperties,
    GGT_PT_MAINPANEL_PT_,
    GGT_PT_MIXAMO_UTILITIES_PT_GGT,
    GGT_PT_TEXTURE_CONTROLS_PT_GGT,
    GGT_PT_BVH_UTILITIES_PT_GGT,
    GGT_PT_ARMATURE_UTILITIES_PT_GGT,
    GGT_PT_ROOT_MOTION_PT_GGT,
    GGT_PT_ANIMATIONS_PT_GGT,
    GGT_PT_TILESET_GENERATOR_PT_GGT,
    ACTION_UL_list,
    INIT_CHARACTER_OT,
    JOIN_ANIMATIONS_OT,
    RENAME_RIG_OT,
    PREPARE_RIG_OT,
    ANIMATION_PLAYER_OT,
    STOP_ANIMATION_OT,
    NLA_TRACKS_OT,
    RENAME_ANIMATION_OT,
    PROCESS_ACTIONS_OT,
    ADD_ROOTBONE_OT,
    ADD_ROOTMOTION_OT,
    UPDATE_ROOTMOTION_OT,
    SAVE_BAKE_TEXTURES_OT,
    BAKE_TEXTURE_OT,
    CREATE_BAKE_TEXTURES_OT,
    TILESET_EXPORT_GODOT_TILESET_OT,
    TILESET_GENERATE_TILE_OT,
    TILESET_SET_ISOMETRIC_CAMERA_OT,
    TILESET_SET_TOPDOWN_CAMERA_OT,
    TILESET_MOVE_CAMERA_TILE_OT,
    TILESET_ADD_COLLISION_SHAPE_OT,
    TILESET_REMOVE_COLLISION_SHAPE_OT,
    TILESET_ADD_NAVIGATION_SHAPE_OT,
    TILESET_REMOVE_NAVIGATION_SHAPE_OT,
    TILESET_ADD_RENDER_SETUP_OT
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.godot_game_tools = PointerProperty(type=AddonProperties, name="Godot Game Tools")
    bpy.types.Action.ggt_props = PointerProperty(type=ActionProperties, name="GGT Action")
    bpy.types.Scene.action_list_index = bpy.props.IntProperty(update=update_action_list)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.godot_game_tools
    del bpy.types.Action.ggt_props
    del bpy.types.Scene.action_list_index

if __name__ == "__main__":
    register()
