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
        hips_scale = tool.hips_scale
        actions = bpy.data.actions
        for action in actions:
            action.groups[0].name = action.name
            for f in action.fcurves:
               if f.data_path == 'pose.bones[\"{}\"].location'.format(tool.rootmotion_hip_bone):
                    for keyframe in f.keyframe_points:
                        keyframe.co[1] *= hips_scale
                # print("Action {} hips are scaled to 0.01.".format(action.name))
            action.ggt_props.hips_scale = hips_scale
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

class GGT_OT_TRIM_ANIMATION_OT_GGT(Operator):
    bl_idname = "wm_ggt.trim_animation"
    bl_label = "Trim Animation"
    bl_description = "Trim Selected Animation Into A New One"

    def copyKeyFramePoints(self, fcurveList, targetAction, targetActionName):
        for curveSrc in fcurveList:
            newFcurve = targetAction.fcurves.new(data_path=curveSrc.data_path, index=curveSrc.array_index, action_group=targetActionName)
            keyframePoints = curveSrc.keyframe_points
            totalFrames = len(keyframePoints)
            newFcurve.keyframe_points.add(totalFrames)
            for i, keyframe_point in enumerate(keyframePoints):
                newFcurve.keyframe_points[i].co = keyframe_point.co

    def trimAnimation(self, targetAction, fromFrame, toFrame, character):
        for group in targetAction.groups:
            if not group.select: continue
            channels = group.channels
            for channel in channels:
                keyframePoints = channel.keyframe_points
                if not channel.select: continue
                deleteFrameList = []
                newIndex = 1
                for i in range(0, len(keyframePoints)):
                    frame = keyframePoints[i].co[0]
                    if frame >= fromFrame and frame <= toFrame:
                        keyframePoints[i].co[0] = float(newIndex)
                        newIndex += 1
                    else:
                        deleteFrameList.append(frame)
                for deleteFrame in deleteFrameList:
                    character.keyframe_delete(channel.data_path, frame=deleteFrame, index=channel.array_index)
                bpy.context.scene.frame_start = 0
                bpy.context.scene.frame_end = newIndex - 1

    def filterCurve(self, obj, curveType):
        fCurves = []
        if obj.type in ['MESH','ARMATURE'] and obj.animation_data:
            fCurves = [fc for fc in obj.animation_data.action.fcurves for type in curveType if fc.data_path.endswith(type)]
        return fCurves

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        character = tool.target_object
        newActionName = tool.trim_animation_name
        fromFrame = tool.trim_animation_from
        toFrame = tool.trim_animation_to
        selectedAction = character.animation_data.action
        animFramesSize = int(selectedAction.frame_range[-1])
        if (character is None): character = bpy.context.view_layer.objects.active

        if character.type in ['ARMATURE'] and character.animation_data and newActionName:

            if fromFrame < animFramesSize and toFrame < animFramesSize:
                # Available Curves ("location", "rotation", "scale")
                fcurveList = self.filterCurve(character, ("location"))
                bpy.data.actions.new(newActionName)
                newAnimation = [anim for anim in bpy.data.actions.keys() if anim in (newActionName)]
                newAnimationIndex = bpy.data.actions.keys().index(newActionName)
                character.animation_data.action = bpy.data.actions.values()[newAnimationIndex]
                targetAction = character.animation_data.action
                # Copy Animation Keyframes
                self.copyKeyFramePoints(fcurveList, targetAction, newActionName)
                # Trim Animation Frames Choosen By User
                self.trimAnimation(targetAction, fromFrame, toFrame, character)

                self.report({'INFO'}, 'New Animation Added')
            else:
                self.report({'INFO'}, 'Choose Valid Animation Frames')
        else:
            self.report({'INFO'}, 'Choose Valid Animation Trim Settings')

        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_DELETE_ANIMATION_OT_GGT(Operator):
    bl_idname = "wm_ggt.delete_animation"
    bl_label = "Delete Current Animation"
    bl_description = "Deletes Current Selected Animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        character = tool.target_object
        animation = tool.animations
        selectedAction = character.animation_data.action
        if (character is None): character = bpy.context.view_layer.objects.active
        if len(bpy.data.actions) > 0 and selectedAction:
            bpy.data.actions.remove(selectedAction)
            self.report({'INFO'}, 'Animation Deleted')
        else:
            self.report({'INFO'}, 'Select Animation to Delete')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
