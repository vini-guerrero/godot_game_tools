import bpy
import os

from bpy.types import (Operator)

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
                self.report({'INFO'}, 'NLA Tracks Generated')
            else:
                self.report({'INFO'}, 'Select A Valid Armature With Animation Data')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_CHARACTER_EXPORT_GGT(Operator):
    bl_idname = "wm_ggt.character_export"
    bl_label = "Export Character as GLTF"
    bl_description = "Exports character to Godot Engine"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        bpy.ops.wm_ggt.push_nlas('EXEC_DEFAULT')
        if (target_armature is None): target_armature = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target_armature
        character_export_path = tool.character_export_path
        fileName = os.path.join(bpy.path.abspath(character_export_path), target_armature.name)
        bpy.ops.export_scene.gltf(filepath=fileName, export_format="GLB", export_frame_range=False, export_force_sampling=False, export_tangents=False, export_image_format="JPEG", export_cameras=False, export_lights=False)
        return {'FINISHED'}
