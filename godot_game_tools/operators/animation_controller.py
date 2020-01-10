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
        target_armature = tool.target_object
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        bpy.context.scene.frame_start = 1
        if len(bpy.data.actions) > 0:
            bpy.ops.screen.animation_play()
            self.report({'INFO'}, 'Playing Animation')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class STOP_ANIMATION_OT(Operator):
    bl_idname = "wm.animation_stop"
    bl_label = "Stop Animation"
    bl_description = "Stops current animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        bpy.context.scene.frame_current = 0
        bpy.ops.screen.animation_cancel(0)
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

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class PROCESS_ACTIONS_OT(Operator):
    bl_idname = "scene.process_actions"
    bl_label = "Update Imported Animations"
    bl_description = "Run to process all actions in the scene. ( Rename and scale bones etc..)"

    def execute(self, context):
        actions = bpy.data.actions
        for action in actions:
            action.groups[0].name = action.name
            if action.ggt_props.hips_scale == 1.0:
                for f in action.fcurves:
                    if f.data_path == 'pose.bones["Hips"].location':
                        for keyframe in f.keyframe_points:
                            keyframe.co[1] *= .01
                print("Action {} hips are scaled to 0.01.".format(action.name))
                action.ggt_props.hips_scale = 0.01
        return {'FINISHED'}
