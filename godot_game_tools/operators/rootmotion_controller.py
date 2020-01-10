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
    bl_label = "Update Root Motion"
    bl_description = "Updates Root Motion Bone To Animation"

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
                add_root_curves(target_armature.animation_data.action)
                bpy.ops.wm.update_rootmotion('EXEC_DEFAULT')
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, 'Root Motion Added')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class UPDATE_ROOTMOTION_OT(Operator):
    bl_idname = "wm.update_rootmotion"
    bl_label = "Update Root Motion"
    bl_description = "Updates Root Motion For Animation"

    def execute(self, context):
        tool = bpy.context.scene.godot_game_tools
        target_object = tool.target_object
        root_motion_name = tool.rootmotion_name
        action = target_object.animation_data.action
        use_root = target_object.animation_data.action.ggt_props.use_root_motion
        use_z = target_object.animation_data.action.ggt_props.use_root_motion_z

        #add_root_curves(target_object.animation_data.action)

        # Root Motion
        for f in action.fcurves:
            if f.data_path == 'pose.bones["{}"].location'.format(tool.rootmotion_name):
                # root x
                if f.array_index == 0:
                    if use_root:
                        f.mute = False
                    else:
                        f.mute = True
                # root y
                if f.array_index == 1:
                    if use_z and use_root:
                        f.mute = False
                    else:
                        f.mute = True
                # root z
                if f.array_index == 2:
                    if use_root:
                        f.mute = False
                    else:
                        f.mute = True
        # Hips
        if use_root:
            action.fcurves[0].mute = True
        else:
            action.fcurves[0].mute = False
        if use_z and use_root:
            action.fcurves[1].mute = True
        else:
            action.fcurves[1].mute = False
        if use_root:
            action.fcurves[2].mute = True
        else:
            action.fcurves[2].mute = False

        self.report({'INFO'}, "Root motion for action {} set to {} z: {}".format(action.name, use_root, use_z))
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def add_root_curves(action: bpy.types.Action):
    rootmotion_name = bpy.context.scene.godot_game_tools.rootmotion_name
    if action.fcurves.find('pose.bones["{}"].location'.format(rootmotion_name)) is None:
        x_curve = action.fcurves.new(data_path='pose.bones["{}"].location'.format(rootmotion_name), index=0, action_group="RootMotion")
        x_hips = action.fcurves[0]
        x_offset = x_hips.keyframe_points[0].co[1]
        for frame_index, keyframe_point in enumerate(x_hips.keyframe_points):
            kf = x_curve.keyframe_points.insert(frame=keyframe_point.co[0], value=keyframe_point.co[1]-x_offset, options={'FAST'}, keyframe_type='KEYFRAME')
            kf.interpolation = 'LINEAR'
        y_curve = action.fcurves.new(data_path='pose.bones["{}"].location'.format(rootmotion_name), index=1, action_group="RootMotion")
        y_hips = action.fcurves[1]
        y_offset = y_hips.keyframe_points[0].co[1]
        for frame_index, keyframe_point in enumerate(y_hips.keyframe_points):
            kf = y_curve.keyframe_points.insert(frame=keyframe_point.co[0], value=keyframe_point.co[1]-y_offset, options={'FAST'}, keyframe_type='KEYFRAME')
            kf.interpolation = 'LINEAR'
        z_curve = action.fcurves.new(data_path='pose.bones["{}"].location'.format(rootmotion_name), index=2, action_group="RootMotion")
        z_hips = action.fcurves[2]
        z_offset = z_hips.keyframe_points[0].co[1]
        for frame_index, keyframe_point in enumerate(z_hips.keyframe_points):
            kf = z_curve.keyframe_points.insert(frame=keyframe_point.co[0], value=keyframe_point.co[1]-z_offset, options={'FAST'}, keyframe_type='KEYFRAME')
            kf.interpolation = 'LINEAR'
        print('Added Root Motion Curves to action {}'.format(action.name))
