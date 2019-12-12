import bpy

from bpy.types import (Operator)

class ADD_ROOTBONE_OT(Operator):
    bl_idname = "wm.add_rootbone"
    bl_label = "Add Root Bone"
    bl_description = "Adds armature root bone for root motion"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        rootMotionBoneName = tool.rootmotion_name
        if not target_armature:
            self.report({'INFO'}, 'Please select a valid armature')
        if target_armature.type == 'ARMATURE':
            # Validates Required Bone Exists In Armature
            createRootMotionBone = True
            if len(target_armature.data.bones) > 0:
                for bone in target_armature.data.bones:
                    if bone.name == rootMotionBoneName:
                        createRootMotionBone = False
                if createRootMotionBone:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.armature.bone_primitive_add(name=rootMotionBoneName)
                    rootMotionBone = target_armature.data.edit_bones[rootMotionBoneName]
                    # Insert Location on RootMotion Bone
                    bpy.ops.object.mode_set(mode="POSE")
                    bpy.context.view_layer.objects.active.data.bones[rootMotionBoneName].select = True
                    scene.frame_set(0)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    # Parent Bone
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    hipsBone = target_armature.data.edit_bones["Hips"]
                    rootMotionBone = target_armature.data.edit_bones[rootMotionBoneName]
                    target_armature.data.edit_bones.active = rootMotionBone
                    rootMotionBone.select = False
                    hipsBone.select = True
                    rootMotionBone.select = True
                    bpy.ops.armature.parent_set(type='OFFSET')
                    bpy.ops.object.mode_set(mode='OBJECT')
        else:
            self.report({'INFO'}, 'Please select the armature')
        self.report({'INFO'}, 'Root Bone Added')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class ADD_ROOTMOTION_OT(Operator):
    bl_idname = "wm.add_rootmotion"
    bl_label = "Add Root Motion"
    bl_description = "Adds Root Motion Bone To Animation"

    def get_fcurve(self, armature, bone_name):
      result = None
      for fcurve in armature.animation_data.action.fcurves:
        fcurve_split = fcurve.data_path.split('"')
        if fcurve_split[1] == bone_name and fcurve_split[2] == "].location":
          result = fcurve
          break
      return result

    def execute(self, context):

        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        rootMotionBoneName = tool.rootmotion_name
        rootmotion_all = tool.rootmotion_all
        animationsForRootMotion = []
        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(bpy.context.object.animation_data.action)
        bpy.ops.wm.add_rootbone('EXEC_DEFAULT')

        if len(bpy.data.actions) > 0:
            for action in animationsForRootMotion:
                animation = action.name
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                # Insert Location on RootMotion Bone
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode="POSE")
                anim_root_bone = target_armature.pose.bones[rootMotionBoneName]
                anim_hip_bone = target_armature.pose.bones["Hips"]
                scene.frame_set(1)
                anim_root_bone.keyframe_insert(data_path='location')
                hip_fcurve = self.get_fcurve(target_armature, "Hips")
                frames = []
                for point in hip_fcurve.keyframe_points[1:]:
                    frames.append(point.co[0])
                for index in frames:
                    scene.frame_set(index)
                    anim_root_bone.location = anim_hip_bone.location
                    anim_root_bone.keyframe_insert(data_path='location')
                    anim_hip_bone.keyframe_delete(data_path='location')
                    #hip_fcurve.location[0].mute = True
                    #hip_fcurve.location[2].mute = True
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, 'Root Motion Added')
        return {'FINISHED'}

def enable_root_motion( action: bpy.types.Action, use_z_axis = False ) -> bool:

    root_bone_name = bpy.context.scene.godot_game_tools.target.name.rootmotion_name
    #target_armature =

    animation_id = bpy.data.actions.keys().index(action.name)
    end_frame = action.frame_range[-1]

    return True











