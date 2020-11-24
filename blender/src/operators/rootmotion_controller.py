import bpy

from bpy.types import (Operator)

class GGT_OT_ADD_ROOTBONE_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_rootbone"
    bl_label = "Add Root Bone"
    bl_description = "Adds armature root bone for root motion"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_object
        rootMotionBoneName = tool.rootmotion_name
        rootmotionStartFrame = tool.rootMotion_start_frame
        rootMotionBoneOffset = 1
        hips = tool.rootmotion_hip_bone
        armatureVisible = target_armature.hide_viewport
        # target_armature.hide_viewport = False
        # bpy.context.object.show_in_front = False

        if not target_armature:
            self.report({'INFO'}, 'Please select a valid armature')

        # Bones
        if hips == '' or hips is None:
            self.report({'ERROR'}, 'Please select a root motion bone, e.g. the hips of your character')
            return {'CANCELLED'}

        if target_armature.type == 'ARMATURE':
            # Validates Required Bone Exists In Armature
            if len(target_armature.data.bones) > 0:
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.context.view_layer.objects.active = target_armature
                if not rootMotionBoneName in target_armature.data.edit_bones:
                    hipsBone = target_armature.data.edit_bones[hips]
                    # Bone Setup
                    rootMotionBone = target_armature.data.edit_bones.new(rootMotionBoneName)
                    rootMotionBone.tail = hipsBone.tail
                    rootMotionBone.head = hipsBone.head
                    rootMotionBone.head.y -= rootMotionBoneOffset
                    rootMotionBone.tail.y -= rootMotionBoneOffset
                    # rootMotionBone.tail.z = 0.2
                    # rootMotionBone.head.y = -0.5
                    target_armature.data.edit_bones[hips].parent = rootMotionBone
                    bpy.ops.object.mode_set(mode="POSE")
                    bpy.context.view_layer.objects.active.data.bones[rootMotionBoneName].select = True
                    scene.frame_set(rootmotionStartFrame)
                    bpy.ops.anim.keyframe_insert_menu(type='Location')
                    bpy.ops.object.mode_set(mode='OBJECT')
        else:
            self.report({'INFO'}, 'Please select the armature')
        self.report({'INFO'}, 'Root Bone Added')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_ADD_ROOTMOTION_LEGACY_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_rootmotion_legacy"
    bl_label = "Add Root Motion"
    bl_description = "Adds Root Motion Bone To Animations"

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
        rootmotionStartFrame = tool.rootMotion_start_frame
        # Call Operator From Outside Class
        animationsForRootMotion = []
        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(bpy.context.object.animation_data.action)
        bpy.ops.wm_ggt.add_rootbone()
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
                scene.frame_set(rootmotionStartFrame)
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
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, 'Root Motion Added')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_ADD_ROOTMOTION_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_rootmotion"
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
        hips = tool.rootmotion_hip_bone
        anim_hip_bone = target_armature.pose.bones[hips]
        animationsForRootMotion = []
        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(bpy.context.object.animation_data.action)
        try:
            bpy.ops.wm_ggt.add_rootbone('EXEC_DEFAULT')
        except RuntimeError:
            self.report({'ERROR'}, 'Could not add root motion, please check your root motion bone.')
            return {'CANCELLED'}

        if len(bpy.data.actions) > 0:
            for action in animationsForRootMotion:
                animation = action.name
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                add_root_curves(target_armature.animation_data.action)
                bpy.ops.wm_ggt.update_rootmotion('EXEC_DEFAULT')
                # deleteCurvesLocation(anim_hip_bone, hips, target_armature.animation_data.action)
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, 'Root Motion Added')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_UPDATE_ROOTMOTION_OT_GGT(Operator):
    bl_idname = "wm_ggt.update_rootmotion"
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
        # print('Added Root Motion Curves to action {}'.format(action.name))

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def deleteCurvesLocation(skeletonBone, boneName, action: bpy.types.Action):
    frames = []
    if boneName and anim_hip_bone:
        searchCurve = action.fcurves.find('pose.bones["{}"].location'.format(boneName))
        for point in searchCurve.keyframe_points[1:]: frames.append(point.co[0])
        for index in frames:
              bpy.context.scene.frame_set(index)
              skeletonBone.keyframe_delete(data_path='location')

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_ADD_ROOTMOTION_TOGGLE_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_rootmotion_toggle"
    bl_label = "Add Root Motion"
    bl_description = "Adds Root Motion Bone To Animations"

    def getCurve(self, obj, bone):
        fCurves = []
        filter = 'pose.bones["{}"].location'.format(bone)
        if obj.type in ['MESH','ARMATURE'] and obj.animation_data:
            fCurves = [fc for fc in obj.animation_data.action.fcurves if fc.data_path == filter]
        return fCurves

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        rootMotionBoneName = tool.rootmotion_name
        rootmotion_all = tool.rootmotion_all
        rootmotionStartFrame = tool.rootMotion_start_frame
        rootmotion_animation_air_fix = tool.rootmotion_animation_air_fix
        animationsForRootMotion = []
        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(bpy.context.object.animation_data.action)

        boneExists = rootMotionBoneName in target_armature.pose.bones.keys()
        hips = tool.rootmotion_hip_bone
        anim_hip_bone = target_armature.pose.bones[hips]
        action = bpy.context.object.animation_data.action
        actionName = action.name

        if not boneExists: bpy.ops.wm_ggt.add_rootbone()

        if len(bpy.data.actions) > 0:
            for action in animationsForRootMotion:
                animation = action.name
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]

                anim_root_bone = target_armature.pose.bones[rootMotionBoneName]
                scene.frame_set(rootmotionStartFrame)
                offsetHipsLocation = anim_root_bone.location - anim_hip_bone.location

                if rootmotion_animation_air_fix:
                    scene.frame_set(rootmotionStartFrame)
                    anim_hip_bone.location.y = 0
                    anim_hip_bone.keyframe_insert(data_path='location')

                hipsFCurves = self.getCurve(target_armature, hips)
                for fcurve in hipsFCurves:
                    frames = []
                    for point in fcurve.keyframe_points[1:]: frames.append(point.co[0])

                    if not tool.motion_axis[fcurve.array_index]:
                        continue
                    for index in frames:
                        scene.frame_set(index)
                        anim_root_bone.location = anim_hip_bone.location + offsetHipsLocation
                        anim_root_bone.keyframe_insert(data_path='location', index=fcurve.array_index)
                        anim_hip_bone.keyframe_delete(data_path='location', index=fcurve.array_index)

                rootMotionFCurves = self.getCurve(target_armature, tool.rootmotion_name)

                for fcurve in rootMotionFCurves:
                    frames = []
                    for point in fcurve.keyframe_points[1:]: frames.append(point.co[0])

                    if tool.motion_axis[fcurve.array_index]:
                        continue
                    for index in frames:
                        scene.frame_set(index)
                        anim_hip_bone.location = anim_root_bone.location - offsetHipsLocation
                        anim_root_bone.keyframe_delete(data_path='location', index=fcurve.array_index)
                        anim_hip_bone.keyframe_insert(data_path='location', index=fcurve.array_index)


        self.report({'INFO'}, 'Root Motion Updated')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
