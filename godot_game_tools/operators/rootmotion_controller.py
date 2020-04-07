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
        rootmotionStartFrame = tool.rootMotionStartFrame
        hips = tool.rootmotion_hip_bone
        armatureVisible = target_armature.hide_viewport
        target_armature.hide_viewport = False
        bpy.context.object.show_in_front = False

        if not target_armature:
            self.report({'INFO'}, 'Please select a valid armature')

        # Bones
        if hips == '' or hips is None:
            self.report({'ERROR'}, 'Please select a root motion bone, e.g. the hips of your character')
            return {'CANCELLED'}

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
                    # scene.frame_set(rootmotionStartFrame)
                    # bpy.ops.anim.keyframe_insert_menu(type='Location')
                    # Parent Bone
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='EDIT')
                    hipsBone = target_armature.data.edit_bones[hips]
                    rootMotionBone = target_armature.data.edit_bones[rootMotionBoneName]
                    target_armature.data.edit_bones.active = rootMotionBone
                    rootMotionBone.select = False
                    hipsBone.select = True
                    rootMotionBone.select = True
                    bpy.ops.armature.parent_set(type='OFFSET')
                    bpy.ops.object.mode_set(mode='OBJECT')
                    target_armature.hide_viewport = not armatureVisible
                    bpy.context.object.show_in_front = not armatureVisible
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
        rootmotionStartFrame = tool.rootMotionStartFrame
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

class GGT_OT_ADD_ROOTMOTION_TOGGLE_OT_GGT(Operator):
    bl_idname = "wm_ggt.add_rootmotion_toggle"
    bl_label = "Update Root Motion"
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
        rootmotionStartFrame = tool.rootMotionStartFrame
        animationsForRootMotion = []
        muteCurvesHips = []
        muteCurvesRootMotion = []

        # Toggles
        # Hips
        root_motion_hips_x_channel = tool.root_motion_hips_x_channel
        root_motion_hips_y_channel = tool.root_motion_hips_y_channel
        root_motion_hips_z_channel = tool.root_motion_hips_z_channel
        # RootMotion
        root_motion_rootmotion_x_channel = tool.root_motion_rootmotion_x_channel
        root_motion_rootmotion_y_channel = tool.root_motion_rootmotion_y_channel
        root_motion_rootmotion_z_channel = tool.root_motion_rootmotion_z_channel

        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(target_armature.animation_data.action)

        if not root_motion_hips_x_channel: muteCurvesHips.append(0)
        if not root_motion_hips_y_channel: muteCurvesHips.append(1)
        if not root_motion_hips_z_channel: muteCurvesHips.append(2)

        if not root_motion_rootmotion_x_channel: muteCurvesRootMotion.append(0)
        if not root_motion_rootmotion_y_channel: muteCurvesRootMotion.append(1)
        if not root_motion_rootmotion_z_channel: muteCurvesRootMotion.append(2)

        # Validations
        boneExists = rootMotionBoneName in target_armature.pose.bones.keys()
        rootMotionBoneName = tool.rootmotion_name
        hips = tool.rootmotion_hip_bone
        anim_hip_bone = target_armature.pose.bones[hips]
        rootmotionStartFrame = tool.rootMotionStartFrame

        if len(bpy.data.actions) > 0:
            for action in animationsForRootMotion:
                animation = action.name
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]

                action = bpy.context.object.animation_data.action
                actionName = animation

                if not boneExists: bpy.ops.wm_ggt.add_rootbone()
                scene.frame_set(rootmotionStartFrame)

                checkRootMotionCurves = self.getCurve(target_armature, rootMotionBoneName)
                if len(checkRootMotionCurves) < 1:

                        prefix = 'pose.bones["{}"].'.format(rootMotionBoneName)
                        fCurves = action.fcurves
                        xCurve = fCurves.new(prefix + 'location', index=0, action_group=actionName)
                        yCurve = fCurves.new(prefix + 'location', index=1, action_group=actionName)
                        zCurve = fCurves.new(prefix + 'location', index=2, action_group=actionName)

                        anim_root_bone = target_armature.pose.bones[rootMotionBoneName]
                        rootMotionAxis = [1, 2, 3]

                        for group in action.groups:
                            if not group.select: continue
                            channels = group.channels
                            for channel in channels:

                                keyframePointsRootMotion = []
                                fCurveBone = channel.data_path.split('"')[1]
                                locationFilter = channel.data_path.split('"')[2]
                                curveIndex = channel.array_index

                                if fCurveBone == hips and curveIndex in rootMotionAxis and locationFilter == "].location":
                                    keyframePoints = channel.keyframe_points
                                    for i in range(0, len(keyframePoints)):
                                        keyframePointsRootMotion.append(keyframePoints[i])
                                else:

                                    if fCurveBone == rootMotionBoneName and curveIndex in rootMotionAxis and locationFilter == "].location":
                                        totalFrames = len(keyframePoints)
                                        channel.keyframe_points.add(totalFrames)
                                        for frame in keyframePoints:
                                            index = int(frame.co[0]) - 1
                                            channel.keyframe_points[index].co[0] = frame.co[0]
                                            channel.keyframe_points[index].co[1] = frame.co[1]

                filterHipsCurves = self.getCurve(target_armature, hips)
                for curve in filterHipsCurves:
                    if curve.array_index in muteCurvesHips: curve.mute = True
                    else: curve.mute = False

                filterRootMotionCurves = self.getCurve(target_armature, rootMotionBoneName)
                for curve in filterRootMotionCurves:
                    if curve.array_index in muteCurvesRootMotion: curve.mute = True
                    else: curve.mute = False

        self.report({'INFO'}, 'Root Motion Updated')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
