import bpy

from bpy.types import (Operator)

class NLA_TRACKS_OT(Operator):
    bl_idname = "wm.push_nlas"
    bl_label = "Create NLA Tracks"
    bl_description = "Push All Animations to NLA Tracks"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        bpy.context.scene.frame_start = 2
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                animation = action.name
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                bpy.context.area.ui_type = 'NLA_EDITOR'
                bpy.ops.nla.action_pushdown(channel_index=1)
        bpy.context.area.ui_type = 'VIEW_3D'
        self.report({'INFO'}, 'NLA Tracks Generated')
        return {'FINISHED'}
