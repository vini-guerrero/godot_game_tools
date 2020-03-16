import bpy
import os

from bpy.types import (Operator)

class GGT_OT_NLA_TRACKS_OT_GGT(Operator):
    bl_idname = "wm_ggt.push_nlas"
    bl_label = "Create NLA Tracks"
    bl_description = "Push All Animations to NLA Tracks"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        export_t_pose = tool.export_t_pose
        target_armature = tool.target_object
        bpy.ops.screen.animation_cancel()
        if (target_armature is None): target_armature = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target_armature
        if len(bpy.data.actions) > 0:
            if hasattr(target_armature, 'animation_data'):
                animations = bpy.data.actions
                for action in animations:
                    if target_armature.animation_data is not None:
                        if action is not None:
                            if export_t_pose:
                                track = target_armature.animation_data.nla_tracks.new()
                                track.strips.new(action.name, bpy.context.scene.frame_start, action)
                                track.name = action.name
                            else:
                                skip = False
                                if action.name == "T-Pose": skip = True
                                elif action.name == "T-Pose-loop": skip = True
                                if not skip:
                                    track = target_armature.animation_data.nla_tracks.new()
                                    track.strips.new(action.name, bpy.context.scene.frame_start, action)
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
    bl_label = "Export Character"
    bl_description = "Exports character to Godot Engine"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        if (target_armature is None): target_armature = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = target_armature
        character_export_path = tool.character_export_path
        fileName = os.path.join(bpy.path.abspath(character_export_path), target_armature.name)
        # bpy.context.area.ui_type = 'NLA_EDITOR'
        # bpy.ops.anim.channels_select_all(action='SELECT')
        # bpy.ops.nla.select_all(action='SELECT')
        # bpy.ops.object.select_all(action='SELECT')
        # bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.export_scene.gltf(filepath=fileName, export_format="GLB", export_tangents=False, export_image_format="JPEG", export_cameras=False, export_lights=False)
        return {'FINISHED'}
