import bpy

from bpy.types import (Operator)

class ANIMATION_PLAYER_OT(Operator):
    bl_idname = "wm.animation_player"
    bl_label = "Play Animation"
    bl_description = "Play armature animations"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        bpy.context.scene.frame_start = 2
        if len(bpy.data.actions) > 0:
            animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
            animationIndex = bpy.data.actions.keys().index(animation)
            target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
            bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
            bpy.ops.screen.animation_play()
            self.report({'INFO'}, 'Playing Animation')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class STOP_ANIMATION_OT(Operator):
    bl_idname = "wm.animation_stop"
    bl_label = "Stop Animation"
    bl_description = "Stops curent animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.context.scene.frame_current = 0
        bpy.ops.screen.animation_cancel()
        self.report({'INFO'}, 'Animation Stopped')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


class RENAME_ANIMATION_OT(Operator):
    bl_idname = "wm.rename_animation"
    bl_label = "Rename Current Animation"
    bl_description = "Renames current animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        actionName = tool.action_name
        if len(bpy.data.actions) > 0:
            bpy.context.object.animation_data.action.name = actionName
        self.report({'INFO'}, 'Animation Renamed')
        return {'FINISHED'}
