import bpy
import os
import json
import ast
import glob

from bpy.props import (StringProperty, FloatProperty, PointerProperty, CollectionProperty)
from bpy.types import (Operator, PropertyGroup)
from bpy_extras.io_utils import ImportHelper

class GGT_OT_NLA_TRACKS_OT_GGT(Operator):
    bl_idname = "wm_ggt.push_nlas"
    bl_label = "Create NLA Tracks"
    bl_description = "Push All Animations to NLA Tracks"

    def removeNLATracks(self, context):
        scene = context.scene
        currentScreen = bpy.context.area.ui_type
        bpy.context.area.ui_type = 'NLA_EDITOR'
        bpy.ops.nla.select_all(action='SELECT')
        bpy.ops.nla.tracks_delete()
        bpy.context.area.ui_type = currentScreen

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        character_export_animation_loops = tool.character_export_animation_loops
        target_armature = tool.target_object
        bpy.ops.screen.animation_cancel()
        if (target_armature is None): target_armature = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target_armature
        if len(bpy.data.actions) > 0:
            if hasattr(target_armature, 'animation_data'):
                animations = bpy.data.actions
                self.removeNLATracks(context)
                for action in animations:
                    if target_armature.animation_data is not None:
                        if action is not None:
                            track = target_armature.animation_data.nla_tracks.new()
                            start = action.frame_range[0]
                            track.strips.new(action.name, start, action)
                            track.name = action.name
                            if character_export_animation_loops: track.name += "-loop"
                self.report({'INFO'}, 'NLA Tracks Generated')
            else:
                self.report({'INFO'}, 'Select A Valid Armature With Animation Data')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_CHARACTER_EXPORT_GGT(Operator):
    bl_idname = "wm_ggt.character_export"
    bl_label = "Export Character File"
    bl_description = "Exports character to Godot Engine"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        character_export_create_animation_tree = tool.character_export_create_animation_tree
        animation = tool.animations
        target_armature = tool.target_object
        rootMotionBoneName = tool.rootmotion_name
        character_export_format = int(tool.character_export_format)
        character_export_animation_loops = tool.character_export_animation_loops
        character_name = tool.character_export_character_name if tool.character_export_character_name is not None else target_armature.name
        bpy.ops.wm_ggt.push_nlas('EXEC_DEFAULT')
        if (target_armature is None): target_armature = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target_armature
        character_export_path = tool.character_export_path

        # Generate Filename To Export
        if (character_export_format == 2): character_name += ".dae"
        fileName = os.path.join(bpy.path.abspath(character_export_path), character_name)

        exportFormat = ""
        if (character_export_format == 0): exportFormat = ".gltf"
        if (character_export_format == 1): exportFormat = ".glb"
        if (character_export_format == 2): exportFormat = ".dae"

        # GLTF
        if (character_export_format == 0):
            bpy.ops.export_scene.gltf(filepath=fileName, export_format="GLTF_EMBEDDED", export_frame_range=False, export_force_sampling=False, export_tangents=False, export_image_format="JPEG", export_cameras=False, export_lights=False)

        # GLB
        if (character_export_format == 1):
            bpy.ops.export_scene.gltf(filepath=fileName, export_format="GLB", export_frame_range=False, export_force_sampling=False, export_tangents=False, export_image_format="JPEG", export_cameras=False, export_lights=False)

        # Better Collada
        if (character_export_format == 2):
            bpy.ops.export_scene.dae(check_existing=True, filepath=fileName, filter_glob="*.dae", use_mesh_modifiers=True, use_active_layers=True, use_anim=True, use_anim_action_all=True, use_anim_skip_noexp=True, use_anim_optimize=True, use_copy_images=True)

        # Update Export Character Preset File
        if target_armature["animation_tree_preset"]:
            animation_tree_preset = ast.literal_eval(target_armature["animation_tree_preset"])
            animations = animation_tree_preset["animations"]
            transitions = animation_tree_preset["stateTransitions"]
            states = animation_tree_preset["states"]
            for state in states:
                for transition in transitions:
                    for animation in animations.keys():
                        preset_value = animation
                        animations[animation] = target_armature[animation]
                        updated_value = target_armature[animation]
                        if state["name"] == preset_value: state["name"] = updated_value
                        if transition["from"] == preset_value: transition["from"] = updated_value
                        if transition["to"] == preset_value: transition["to"] = updated_value

            character_data = animation_tree_preset

            # Character Settings
            character_data["characterName"] = character_name
            character_data["meshFileName"] = character_name + exportFormat
            character_data["nodeName"] = "StateMachine"
            character_data["rootMotionBone"] = rootMotionBoneName

            customFileFormat = "json"
            character_json = json.dumps(character_data, sort_keys=True, indent=4)
            character_file = open(fileName + '.' + customFileFormat, 'w+')
            character_file.write(character_json)
            character_file.close()

        self.report({'INFO'}, 'Character File Exported')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_LOAD_ANIMATION_TREE_PRESET_OT_GGT(bpy.types.Operator, ImportHelper):
    bl_idname = "wm_ggt.load_animation_tree_preset"
    bl_label = "Load Animation Tree Preset"
    bl_description = "Select a custom animation tree preset file to export to Godot"
    bl_options = {'REGISTER', 'UNDO'}
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        with open(self.filepath, 'r+') as f:
            # Remove Previous Properties
            for custom_prop in target_armature.keys(): del target_armature[custom_prop]
            animation_tree_preset = json.load(f)
            target_armature["animation_tree_preset"] = str(animation_tree_preset)
            animation_tree_preset = ast.literal_eval(target_armature["animation_tree_preset"])
            animations = animation_tree_preset["animations"]
            for animation in animations.keys():
                target_armature[animation] = animation_tree_preset["animations"][animation]
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
