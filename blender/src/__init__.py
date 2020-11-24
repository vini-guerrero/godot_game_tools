import bpy
import glob
import os
import sys

from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.props import (IntProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty, BoolVectorProperty, FloatProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)

addon_version = "2.0.4"

bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero & Contributors",
    "version": (2, 0, 4),
    "blender": (2, 90, 0),
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

def validateBetterColladaExporter(self):
    exporterModule = "Better Collada Exporter"
    exporterDetected = False
    modules = []
    for mod_name in bpy.context.preferences.addons.keys():
        mod = sys.modules[mod_name]
        moduleName = mod.bl_info.get('name')
        modules.append(moduleName)
    if exporterModule in modules: exporterDetected = True
    return exporterDetected

def populateExporters(self, context):
    exporters = []
    scene = context.scene
    tool = scene.godot_game_tools
    exporters.append(("0", "GLTF", ""))
    exporters.append(("1", "GLB", ""))
    if tool.better_collada_available: exporters.append(("2", "Better Collada", ""))
    # exporters.append(("3", "FBX", ""))
    return exporters

# ------------------------------------------------------------------------
#    Addon Tool Properties
# ------------------------------------------------------------------------
class GGT_AddonProperties_GGT(PropertyGroup):
    hips_scale: FloatProperty(name="Hips Scale", description="Hips scale factor", default=0.01)
    action_name: StringProperty(name="New Name", description="Choose the action name you want to rename your animation in the dopesheet", maxlen=1024)
    target_object: PointerProperty(name="Armature", description="Select the target armature you want the animations to be merged into", type=bpy.types.Object)
    animations: EnumProperty(name="Animations", description="Available armature animations", items=populateAnimations, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    visible_armature: BoolProperty(name="Show Armature Bones", description="Hides / Show armature bones once animations are loaded", default=True, update=toggleArmatureVisibility)
    bake_texture_size: IntProperty(name="Bake Texture Size", description="Define here the size of textures images to bake", default = 1024, min = 8, max = 4096)
    bake_texture_name: StringProperty(name="Bake Name", description="Select the texture name to be saved", maxlen=1024)
    bake_texture_path: StringProperty(name="Texture Path", description="Select the path destination folder you want textures to be saved", subtype="FILE_PATH")
    bake_filter: EnumProperty(name="Bake Map", description="Choose between available bake maps", items=[('GLOSSY', "GLOSSY", ""),('DIFFUSE', "DIFFUSE", "")], update=None, get=None, set=None)
    character_collection_name: bpy.props.StringProperty(name="Armature Collection Name", default="CharacterCollection")
    # Tileset
    tile_collection_name: bpy.props.StringProperty(name="Tile Collection Name", default="TileCollection")
    tileset_generate_path: StringProperty(name="Tileset Path", description="Select the path destination folder where you want tileset to be exported", subtype="FILE_PATH")
    tileset_tile_width: IntProperty(name="Tile Width", description="Define the desired tiles width", default=32, min=8, max=1024, update=updateTilesetGeneratorCamera, get=None, set=None)
    tileset_tile_height: IntProperty(name="Tile Height", description="Define the desired tiles height", default=32, min=8, max=1024, update=updateTilesetGeneratorCamera, get=None, set=None)
    tileset_type: EnumProperty(name="Tileset Type", description="Choose between available tileset types", items=[('0', "Top-Down", ""),('1', "Isometric", "")], update=updateTilesetGeneratorCamera, get=None, set=None)
    # Godot Project
    character_project_path: StringProperty(name="Project Path", description="Select the root path of your Godot project", subtype="DIR_PATH")
    character_export_path: StringProperty(name="Export Path", description="Select the desired path to export character", subtype="DIR_PATH")
    character_export_character_name: StringProperty(name="Character Name", description="The name of the character, used as name of the export")
    # Exporters
    better_collada_available: BoolProperty(name="Better Collada Exporter", description="Validates if better collada exporter is available", default=False, get=validateBetterColladaExporter)
    character_export_format: EnumProperty(name="Export Format", description="Choose between the best options for quick export to Godot Engine", items=populateExporters, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    trim_animation_name: StringProperty(name="New Animation", description="Choose the new animation name you want for your trim action in the dopesheet", maxlen=1024)
    trim_animation_from: IntProperty(name="From Frame", description="Define the desired start trim frame", default=1, min=0, max=1024, update=None, get=None, set=None)
    trim_animation_to: IntProperty(name="To Frame", description="Define the desired last trim frame", default=1, min=0, max=1024, update=None, get=None, set=None)
    character_export_animation_loops: BoolProperty(name="Add Animation Loops", description="Adds Godot Loop Rename To Exported Animations", default=True, get=None)
    # RootMotion Variables
    rootmotion_name: StringProperty(name="Bone Name", description="Choose name you want for the RootMotion Bone", maxlen=1024, default="RootMotion")
    rootmotion_all: BoolProperty(name="Apply Rootmotion To All", description="Choose to apply rootmotion to all animations or current only", default=False, update=None)
    rootmotion_hip_bone: StringProperty(name="Root Bone", description="Bone which will serve as the basis for the root motion of the character. Usually hips or pelvis")
    rootMotion_start_frame: IntProperty(name="Rootmotion Start Frame", description="Define the initial frame for rootmotion start", default=1, min=-1, max=1024, update=None, get=None, set=None)
    rootmotion_animation_air_fix: BoolProperty(name="In Air Fix", description="Optional workaround to fix animations that start with character in-air", default=False, update=None)
    motion_axis: BoolVectorProperty(name="Motion Axis", description="Optional workaround to make root motion only in select local axis", update=None, subtype='XYZ')
    # Animation Actions
    character_export_create_animation_tree: BoolProperty(name="Create Animation Tree", description="Whether or not an animation tree is created when exporting as a Godot scene")
    actions = []

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

# ------------------------------------------------------------------------
#    Action Properties
# ------------------------------------------------------------------------
class GGT_ActionProperties_GGT(bpy.types.PropertyGroup):
    use_root_motion: BoolProperty(name="Root Motion", description="Should this animation use root motion", options={'ANIMATABLE'}, default=True, update=toggle_use_root_motion)
    use_root_motion_z: BoolProperty(name="Root Motion Z", description="Use z-axis with this animation", default=False, update=toggle_use_root_motion_z)

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
from .operators.export_character_controller import (
    GGT_OT_NLA_TRACKS_OT_GGT,
    GGT_OT_CHARACTER_EXPORT_GGT,
    GGT_OT_LOAD_ANIMATION_TREE_PRESET_OT_GGT
)
from .operators.animation_controller import (
    GGT_OT_ANIMATION_PLAYER_OT_GGT,
    GGT_OT_STOP_ANIMATION_OT_GGT,
    GGT_OT_RENAME_ANIMATION_OT_GGT,
    GGT_OT_PROCESS_ACTIONS_OT_GGT,
    GGT_OT_ADD_ANIMATION_LOOP_OT_GGT,
    GGT_OT_TRIM_ANIMATION_OT_GGT,
    GGT_OT_DELETE_ANIMATION_OT_GGT
)
from .operators.rootmotion_controller import (
    GGT_OT_ADD_ROOTBONE_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_OT_GGT,
    GGT_OT_UPDATE_ROOTMOTION_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_LEGACY_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_TOGGLE_OT_GGT
)
from .operators.character_controller import (
    GGT_OT_INIT_CHARACTER_OT_GGT,
    GGT_OT_JOIN_ANIMATIONS_OT_GGT,
    GGT_OT_PREPARE_RIG_OT_GGT,
    GGT_OT_RENAME_RIG_OT_GGT,
    GGT_OT_ARMATURE_JOIN_MESH_GGT
)
from .operators.texture_controller import (
    GGT_OT_BAKE_TEXTURE_OT_GGT,
    GGT_OT_CREATE_BAKE_TEXTURES_OT_GGT,
    GGT_OT_SAVE_BAKE_TEXTURES_OT_GGT
)
from .operators.tileset_controller import (
    GGT_OT_TILESET_GENERATE_TILE_OT_GGT,
    GGT_OT_TILESET_SET_ISOMETRIC_CAMERA_OT_GGT,
    GGT_OT_TILESET_SET_TOPDOWN_CAMERA_OT_GGT,
    GGT_OT_TILESET_MOVE_CAMERA_TILE_OT_GGT,
    GGT_OT_TILESET_EXPORT_GODOT_TILESET_OT_GGT,
    GGT_OT_TILESET_ADD_COLLISION_SHAPE_OT_GGT,
    GGT_OT_TILESET_REMOVE_COLLISION_SHAPE_OT_GGT,
    GGT_OT_TILESET_ADD_NAVIGATION_SHAPE_OT_GGT,
    GGT_OT_TILESET_REMOVE_NAVIGATION_SHAPE_OT_GGT,
    GGT_OT_TILESET_ADD_RENDER_SETUP_OT_GGT
)
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------
#    Panels
# ------------------------------------------------------------------------
# from .panels.bvh_utilities_panel import (
#     GGT_PT_BVH_UTILITIES_PT_GGT
# )
from .panels.texture_controls_panel import (
    GGT_PT_TEXTURE_CONTROLS_PT_GGT
)
from .panels.character_utilities_panel import (
    GGT_PT_CHARACTER_UTILITIES_PT_GGT,
    GGT_PT_ARMATURE_UTILITIES_PT_GGT,
    ACTION_UL_list, GGT_PT_ROOT_MOTION_PT_GGT,
    GGT_PT_ANIMATIONS_PT_GGT,
    GGT_PT_ANIMATION_UTILITIES_PT_GGT,
    GGT_PT_EXPORT_CHARACTER_PT_GGT
)
from .panels.tileset_generator_panel import (
    GGT_PT_TILESET_GENERATOR_PT_GGT
)
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------
#    MAIN ADD-ON PANEL
# ------------------------------------------------------------------------
class GGT_PT_MAINPANEL_PT_(Panel):
    bl_idname = "obj_ggt.main_panel"
    bl_label = "Godot Game Tools - v" + addon_version
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Godot Game Tools"
    bl_context = "objectmode"
    def draw(self, context): pass

# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------
classes = (
    # Default Add-On Properties
    GGT_AddonProperties_GGT,
    GGT_ActionProperties_GGT,
    # Panels
    GGT_PT_MAINPANEL_PT_,
    GGT_PT_CHARACTER_UTILITIES_PT_GGT,
    GGT_PT_TEXTURE_CONTROLS_PT_GGT,
    # GGT_PT_BVH_UTILITIES_PT_GGT,
    GGT_PT_ARMATURE_UTILITIES_PT_GGT,
    GGT_PT_ROOT_MOTION_PT_GGT,
    GGT_PT_ANIMATIONS_PT_GGT,
    GGT_PT_ANIMATION_UTILITIES_PT_GGT,
    GGT_PT_EXPORT_CHARACTER_PT_GGT,
    GGT_PT_TILESET_GENERATOR_PT_GGT,
    ACTION_UL_list,
    # Character Controller
    GGT_OT_INIT_CHARACTER_OT_GGT,
    GGT_OT_JOIN_ANIMATIONS_OT_GGT,
    GGT_OT_RENAME_RIG_OT_GGT,
    GGT_OT_PREPARE_RIG_OT_GGT,
    GGT_OT_ARMATURE_JOIN_MESH_GGT,
    # Animation Controller
    GGT_OT_ANIMATION_PLAYER_OT_GGT,
    GGT_OT_STOP_ANIMATION_OT_GGT,
    GGT_OT_RENAME_ANIMATION_OT_GGT,
    GGT_OT_PROCESS_ACTIONS_OT_GGT,
    GGT_OT_ADD_ANIMATION_LOOP_OT_GGT,
    GGT_OT_TRIM_ANIMATION_OT_GGT,
    GGT_OT_DELETE_ANIMATION_OT_GGT,
    # NLA Tracks Controller
    GGT_OT_NLA_TRACKS_OT_GGT,
    GGT_OT_CHARACTER_EXPORT_GGT,
    GGT_OT_LOAD_ANIMATION_TREE_PRESET_OT_GGT,
    # RootMotion Controller
    GGT_OT_ADD_ROOTBONE_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_OT_GGT,
    GGT_OT_UPDATE_ROOTMOTION_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_LEGACY_OT_GGT,
    GGT_OT_ADD_ROOTMOTION_TOGGLE_OT_GGT,
    # Texture Controller
    GGT_OT_BAKE_TEXTURE_OT_GGT,
    GGT_OT_CREATE_BAKE_TEXTURES_OT_GGT,
    GGT_OT_SAVE_BAKE_TEXTURES_OT_GGT,
    # Tileset Controller
    GGT_OT_TILESET_GENERATE_TILE_OT_GGT,
    GGT_OT_TILESET_SET_ISOMETRIC_CAMERA_OT_GGT,
    GGT_OT_TILESET_SET_TOPDOWN_CAMERA_OT_GGT,
    GGT_OT_TILESET_MOVE_CAMERA_TILE_OT_GGT,
    GGT_OT_TILESET_EXPORT_GODOT_TILESET_OT_GGT,
    GGT_OT_TILESET_ADD_COLLISION_SHAPE_OT_GGT,
    GGT_OT_TILESET_REMOVE_COLLISION_SHAPE_OT_GGT,
    GGT_OT_TILESET_ADD_NAVIGATION_SHAPE_OT_GGT,
    GGT_OT_TILESET_REMOVE_NAVIGATION_SHAPE_OT_GGT,
    GGT_OT_TILESET_ADD_RENDER_SETUP_OT_GGT
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.godot_game_tools = PointerProperty(type=GGT_AddonProperties_GGT, name="Godot Game Tools")
    bpy.types.Action.ggt_props = PointerProperty(type=GGT_ActionProperties_GGT, name="GGT Action")
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
