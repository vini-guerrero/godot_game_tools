import bpy

from bpy.types import (Operator)

class GGT_OT_ANIMATION_PLAYER_OT_GGT(Operator):
    bl_idname = "wm_ggt.animation_player"
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

class GGT_OT_STOP_ANIMATION_OT_GGT(Operator):
    bl_idname = "wm_ggt.animation_stop"
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

class GGT_OT_RENAME_ANIMATION_OT_GGT(Operator):
    bl_idname = "wm_ggt.rename_animation"
    bl_label = "Rename Current Animation"
    bl_description = "Renames current animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        actionName = tool.action_name
        if len(bpy.data.actions) > 0:
            target_armature.animation_data.action.name = actionName
        self.report({'INFO'}, 'Animation Renamed')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_PROCESS_ACTIONS_OT_GGT(Operator):
    bl_idname = "scene.process_actions"
    bl_label = "Update Imported Animations"
    bl_description = "Run to process all actions in the scene. ( Rename and scale bones etc..)"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        actions = bpy.data.actions
        for action in actions:
            action.groups[0].name = action.name
            if action.ggt_props.hips_scale == 1.0:
                for f in action.fcurves:
                   if f.data_path == 'pose.bones[\"{}\"].location'.format(tool.rootmotion_hip_bone):
                        for keyframe in f.keyframe_points:
                            keyframe.co[1] *= .01
                # print("Action {} hips are scaled to 0.01.".format(action.name))
                action.ggt_props.hips_scale = 0.01
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_ADD_ANIMATION_LOOP_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_animation_loop"
    bl_label = "Add Godot Animation Loops"
    bl_description = "Adds Godot Loop Rename To Selected Animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        animation = tool.animations
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                action.name += "-loop"
        self.report({'INFO'}, 'Animation Loops Added')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
