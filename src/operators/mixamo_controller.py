import bpy
import glob
import os

from bpy.props import (StringProperty, PointerProperty, CollectionProperty)
from bpy.types import (Operator, PropertyGroup)
from bpy_extras.io_utils import ImportHelper

from ..utils import validateArmature

class INIT_CHARACTER_OT(bpy.types.Operator, ImportHelper):
    """Initializes imported model for the tool"""
    bl_idname = "wm.init_character"
    bl_label = "Initialize Character"
    bl_description = "Used to init 'Main' Armature. Loaded character should have 'T-Pose' animation from mixamo."
    bl_options = {'REGISTER', 'UNDO'}
    expected_filename = "t-pose.fbx"
    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})
    files = CollectionProperty(type=bpy.types.PropertyGroup)

    def import_from_folder(self, path, context):
        extensions = ['fbx']
        filenames = sorted(os.listdir(path))
        valid_files = []
        fileNamesList = []

        for filename in filenames:
            for ext in extensions:
                if filename.lower().endswith('.{}'.format(ext)):
                    valid_files.append(filename)
                    break

        for name in valid_files:
            file_path = os.path.join(path, name)
            #extension = (os.path.splitext(file_path)[1])[1:].lower()

            if ext == "fbx":
                if hasattr(bpy.types, bpy.ops.import_scene.fbx.idname()):
                    action_name, action_extension = os.path.splitext(name)
                    if action_name.lower() == "t-pose":
                        # Local Variable
                        fileNamesList.append(action_name)
                        bpy.ops.import_scene.fbx(filepath = file_path)
                        # print("importing file {}".format(file_path))
                        tool = bpy.context.scene.godot_game_tools
                        tool.target_name = bpy.context.object
                        bpy.context.object.animation_data.action.name = action_name
                        bpy.ops.wm.prepare_mixamo_rig('EXEC_DEFAULT')
                        self.report({'INFO'}, 'T-Pose Loaded')
                        return
                    else:
                        self.report({'INFO'}, 'No T-Pose Found')
                        # print("no t-pose found, skipping {}".format(name))
                        continue

    def execute(self, context):
        self.report({'INFO'}, 'Loading Character T-Pose')
        filePathWithName = bpy.path.abspath(self.properties.filepath)
        path = os.path.dirname(filePathWithName)
        self.import_from_folder(path, context)
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class JOIN_ANIMATIONS_OT(Operator, ImportHelper):
    bl_idname = "wm.join_animations"
    bl_label = "Join Animations"
    bl_description = "Join mixamo animations into a single armature"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".fbx"
    filter_glob: StringProperty(default="*.fbx", options={'HIDDEN'})
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def scale_action(self, action):
        # Scale Hips Down to match the .01 scale on imported model
        fc = action.fcurves
        for f in fc:
            if f.data_path == 'pose.bones["Hips"].location':
                for keyframe in f.keyframe_points:
                    keyframe.co[1] *= .01
        return True

    def importModels(self, path, target_armature, context):
        extensions = ['fbx']
        filenames = sorted(os.listdir(path))
        valid_files = []
        fileNamesList = []
        removeList = []
        # Debug
        removeImports = True

        for filename in filenames:
            for ext in extensions:
                if filename.lower().endswith('.{}'.format(ext)):
                    valid_files.append(filename)
                    break

        for name in valid_files:
            file_path = os.path.join(path, name)
            extension = (os.path.splitext(file_path)[1])[1:].lower()

            if ext == "fbx":
                if hasattr(bpy.types, bpy.ops.import_scene.fbx.idname()):
                    actionName, actionExtension = os.path.splitext(name)
                    if actionName != "T-Pose":
                        # Local Variable
                        fileNamesList.append(actionName)
                        bpy.ops.import_scene.fbx(filepath = file_path)

        if len(bpy.data.collections) > 0:
            for col in bpy.data.collections:
                if len(col.objects) > 0:
                    index = 0
                    for obj in col.objects:
                        if obj.type == "ARMATURE" and obj is not target_armature:
                            print("Importing animation from file {}".format(obj.name))
                            obj.animation_data.action.name = fileNamesList[index]

                            # Rename the bones
                            for bone in obj.pose.bones:
                                if ':' not in bone.name:
                                    continue
                                bone.name = bone.name.split(":")[1]
                            self.scale_action(obj.animation_data.action)

                            removeList.append(obj)
                            index += 1
                            if len(obj.children) > 0:
                                for mesh in obj.children:
                                    removeList.append(mesh)

        # Delete Imported Armatures
        if removeImports:
            objs = [ob for ob in removeList if ob.type in ('ARMATURE', 'MESH')]
            bpy.ops.object.delete({"selected_objects": objs})
            bpy.context.view_layer.objects.active = target_armature

    def setDefaultAnimation(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_name
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                animation = action.name
                if animation in "T-Pose":
                    tool.animations = animation

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_name
        filePathWithName = bpy.path.abspath(self.properties.filepath)
        path = os.path.dirname(filePathWithName)
        bpy.context.object.animation_data.action.name = "T-Pose"
        self.importModels(path, target_armature, context)
        self.setDefaultAnimation(context)
        self.report({'INFO'}, 'Animations Imported Successfully')
        return {'FINISHED'}

<<<<<<< HEAD
from ..utils import validateArmature
=======
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
>>>>>>> upstream/Dev

class RENAME_RIG_OT(Operator):
    bl_idname = "wm.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_name
<<<<<<< HEAD
        valid = validateArmature(bpy.context)
=======
        valid = validateArmature()
>>>>>>> upstream/Dev
        if valid:
            bpy.data.objects["Armature"].select_set(True)
            target_armature.hide_viewport = False
            bpy.ops.object.mode_set(mode='OBJECT')
            if not bpy.ops.object:
                self.report({'INFO'}, 'Please select the armature')
            for rig in bpy.context.selected_objects:
                if rig.type == 'ARMATURE':
                    for mesh in rig.children:
                        for vg in mesh.vertex_groups:
                            # If no ':' probably its already renamed
                            if ':' not in vg.name:
                                continue
                            vg.name = vg.name.split(":")[1]
                    for bone in rig.pose.bones:
                        if ':' not in bone.name:
                            continue
                        bone.name = bone.name.split(":")[1]
            # for action in bpy.data.actions:
            #     fc = action.fcurves
            #     for f in fc:
            #         f.data_path = f.data_path.replace("mixamorig:","")
            if bpy.data.actions:
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
            self.report({'INFO'}, 'Character Bones Successfully Renamed')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

<<<<<<< HEAD

=======
>>>>>>> upstream/Dev
class PREPARE_RIG_OT(Operator):
    bl_idname = "wm.prepare_mixamo_rig"
    bl_label = "Prepare Mixamo Rig"
    bl_description = "Fix mixamo rig to export for Godot"

    def scale_action(self, action):
        # Scale Hips Down to match the .01 scale on imported model
        # To-Do Fix Correct Axis - Jumping Animations Are Currently Breaking Ex: Mixamo (Mutant Jump Attack)
        fc = action.fcurves
        for f in fc:
            if f.data_path == 'pose.bones["Hips"].location':
                for keyframe in f.keyframe_points:
                    keyframe.co[1] *= .01
        return True

<<<<<<< HEAD


    def execute(self, context):

=======
    def execute(self, context):
>>>>>>> upstream/Dev
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_name
        visible_armature = tool.visible_armature
<<<<<<< HEAD
        valid = True
=======
>>>>>>> upstream/Dev
        # Apply transformations on selected Armature
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.wm.rename_mixamo_rig('EXEC_DEFAULT')
<<<<<<< HEAD
=======
        valid = validateArmature()
>>>>>>> upstream/Dev
        if valid:
            bpy.data.objects["Armature"].select_set(True)
            target_armature.hide_viewport = False
            bpy.ops.object.select_all(action='SELECT')
            if len(bpy.data.actions) > 0:
                for anim in bpy.data.actions:
                    animation = anim.name
                    bpy.context.scene.frame_start = 0
                    animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                    animationIndex = bpy.data.actions.keys().index(animation)
                    target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                    bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                    self.scale_action(anim)
            self.report({'INFO'}, 'Rig Armature Prepared')
        return {'FINISHED'}

<<<<<<< HEAD
=======
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

>>>>>>> upstream/Dev
class WM_OT_RENAME_MIXAMORIG(Operator):
    bl_idname = "wm.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_name
<<<<<<< HEAD
        valid = validateArmature(self, context)
=======
        valid = validateArmature()
>>>>>>> upstream/Dev
        if valid:
            bpy.data.objects["Armature"].select_set(True)
            target_armature.hide_viewport = False
            bpy.ops.object.mode_set(mode='OBJECT')
            if not bpy.ops.object:
                self.report({'INFO'}, 'Please select the armature')
            for rig in bpy.context.selected_objects:
                if rig.type == 'ARMATURE':
                    for mesh in rig.children:
                        for vg in mesh.vertex_groups:
                            # If no ':' probably its already renamed
                            if ':' not in vg.name:
                                continue
                            vg.name = vg.name.split(":")[1]
                    for bone in rig.pose.bones:
                        if ':' not in bone.name:
                            continue
                        bone.name = bone.name.split(":")[1]
            # for action in bpy.data.actions:
            #     fc = action.fcurves
            #     for f in fc:
            #         f.data_path = f.data_path.replace("mixamorig:","")
            if bpy.data.actions:
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
            self.report({'INFO'}, 'Character Bones Successfully Renamed')
<<<<<<< HEAD
        return {'FINISHED'}
=======
        return {'FINISHED'}
>>>>>>> upstream/Dev
