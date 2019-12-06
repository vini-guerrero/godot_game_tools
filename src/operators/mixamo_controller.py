import bpy
import glob
import os

from bpy.props import (StringProperty, PointerProperty, CollectionProperty)
from bpy.types import (Operator, PropertyGroup)
from bpy_extras.io_utils import ImportHelper

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
                        # bpy.ops.wm.prepare_mixamo_rig('EXEC_DEFAULT')
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
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})
    files = CollectionProperty(type=bpy.types.PropertyGroup)

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
