import bpy

from bpy.types import (Operator)

class GGT_OT_NLA_TRACKS_OT_GGT(Operator):
    bl_idname = "wm_ggt.push_nlas"
    bl_label = "Create NLA Tracks"
    bl_description = "Push All Animations to NLA Tracks"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        # if len(bpy.data.actions) > 0:
        #     for action in bpy.data.actions:
        #         animation = action.name
        #         animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
        #         animationIndex = bpy.data.actions.keys().index(animation)
        #         target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
        #         bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
        #         bpy.context.area.ui_type = 'DOPESHEET'
        #         bpy.context.space_data.ui_mode = 'ACTION'
        #         bpy.ops.action.push_down()
        #         bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.object.mode_set(mode='OBJECT')
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                if target_armature.animation_data is not None:
                    if action is not None:
                        # bpy.context.scene.frame_start = 0
                        track = target_armature.animation_data.nla_tracks.new()
                        track.strips.new(action.name, bpy.context.scene.frame_start, action)
                        track.name = action.name
        self.report({'INFO'}, 'NLA Tracks Generated')
        return {'FINISHED'}
