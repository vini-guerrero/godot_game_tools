import bpy
import glob
import os
import re

from bpy.props import (StringProperty, FloatProperty, PointerProperty, CollectionProperty)
from bpy.types import (Operator, PropertyGroup)
from bpy_extras.io_utils import ImportHelper

from ..utils import validateArmature

class GGT_OT_INIT_CHARACTER_OT_GGT(bpy.types.Operator, ImportHelper):
    """Initializes imported model for the tool"""
    bl_idname = "wm_ggt.init_character"
    bl_label = "Initialize Character"
    bl_description = "Used to init 'Main' Armature. Loaded character should have 'T-Pose' animation from Mixamo."
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})
    files = CollectionProperty(type=bpy.types.PropertyGroup)
    supported_extensions = ['fbx']

    def import_from_folder(self, file_path, context):
        extension = (os.path.splitext(file_path)[1])[1:].lower()

        if os.path.isdir(file_path):
            return ('ERROR', 'Please select a file containing the T-Pose of your character.')
        elif extension not in self.supported_extensions:
            return ('ERROR', 'The extension of the selected file is not supported. Must be one of the following: ' + ','.join(self.supported_extensions))
        elif hasattr(bpy.types, bpy.ops.import_scene.fbx.idname()):
            bpy.ops.import_scene.fbx(filepath = file_path)
            return ('INFO', 'Import successful')


    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        characterCollectionName = tool.character_collection_name
        if bpy.data.collections.get(characterCollectionName) is None:
          characterCollection = bpy.data.collections.new(characterCollectionName)
          bpy.context.scene.collection.children.link(characterCollection)
        self.report({'INFO'}, 'Loading Character T-Pose')
        filePathWithName = bpy.path.abspath(self.properties.filepath)
        import_result = self.import_from_folder(filePathWithName, context)
        if import_result[0] != 'INFO':
            self.report({import_result[0]}, import_result[1])
            return {'CANCELLED'}

        if bpy.data.collections.get(characterCollectionName) is not None:
            characterArmature = bpy.context.view_layer.objects.active
            if characterArmature == None or characterArmature.type != "ARMATURE":
                self.report({'ERROR'}, 'Imported character does not have a root armature.')
                bpy.ops.collection.objects_remove_all()
                return {'CANCELLED'}

            # Store armature bones
            tool.rootmotion_hip_bone = "Hips" if "Hips" in [re.sub(".*:", "", bone.name) for bone in characterArmature.data.bones] else ""

            characterCollection = bpy.data.collections.get(characterCollectionName)
            if len(characterArmature.children) > 0:
                bpy.ops.collection.objects_remove_all()
                for mesh in characterArmature.children:
                    characterCollection.objects.link(mesh)
            characterCollection.objects.link(characterArmature)
            characterArmature.name = "Armature"
            characterArmature.animation_data.action.name = "T-Pose"
            tool.target_object = characterArmature
        bpy.ops.wm_ggt.prepare_mixamo_rig('EXEC_DEFAULT')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_JOIN_ANIMATIONS_OT_GGT(Operator, ImportHelper):
    bl_idname = "wm_ggt.join_animations"
    bl_label = "Join Animations"
    bl_description = "Join mixamo animations into a single armature"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".fbx"
    filter_glob: StringProperty(default="*.fbx", options={'HIDDEN'})
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def getSelectedFiles(self, file_path, files):
        # If a folder was selected, import all animations of that folder, otherwise only import the selected models
        selected_file_or_path = self.properties.filepath
        if os.path.isdir(selected_file_or_path):
            files = [os.path.join(selected_file_or_path, file) for file in os.listdir(selected_file_or_path)]
        else:
            path = os.path.dirname(selected_file_or_path)
            files = [os.path.join(path, file.name) for file in self.properties.files ]

        for file in files:
            if not os.path.exists(file):
                self.report({'ERROR'}, 'Animation file {} does not exist, skipped import.'.format(file))
                files.remove(file)
        return files

    def importModels(self, file_names, target_armature, context):
        scene = context.scene
        tool = scene.godot_game_tools
        characterCollectionName = tool.character_collection_name
        extensions = ['fbx']
        valid_files = []
        file_names_list = []
        removeList = []
        # Debug
        removeImports = True
        imported_objs = []

        if bpy.data.collections.get(characterCollectionName) is not None:
            characterCollection = bpy.data.collections.get(characterCollectionName)
            for filename in file_names:
                for ext in extensions:
                    if filename.lower().endswith('.{}'.format(ext)):
                        valid_files.append(filename)
                        break

            for file_path in valid_files:
                bpy.ops.object.select_all(action='DESELECT')
                if ext == "fbx":
                    name = os.path.basename(file_path)
                    if hasattr(bpy.types, bpy.ops.import_scene.fbx.idname()):
                        actionName, actionExtension = os.path.splitext(name)
                        if actionName != "T-Pose":
                            # Local Variable
                            file_names_list.append(actionName)
                            bpy.ops.import_scene.fbx(filepath = file_path)
                            imported_objs.append(bpy.context.view_layer.objects.active)

            if len(file_names_list) > 0:
                index = 0
                for obj in imported_objs:
                    obj.animation_data.action.name = file_names_list[index]
                    # Rename the bones
                    for bone in obj.pose.bones:
                        if ':' not in bone.name: continue
                        bone.name = bone.name.split(":")[1]
                    removeList.append(obj)
                    meshes = [obj for obj in obj.children]
                    for mesh in meshes: removeList.append(mesh)
                    index += 1

        # Delete Imported Armatures
        if removeImports:
            objs = [ob for ob in removeList if ob.type in ('ARMATURE', 'MESH')]
            bpy.ops.object.delete({"selected_objects": objs})
            bpy.context.view_layer.objects.active = target_armature

    def setDefaultAnimation(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        if target_armature: target_armature["animation_tree_preset"] = None
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                animation = action.name
                if animation in "T-Pose":
                    tool.animations = animation

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        files = self.getSelectedFiles(self.properties.filepath, self.properties.files)
        self.importModels(sorted(files), target_armature, context)
        bpy.ops.scene.process_actions('EXEC_DEFAULT')
        self.setDefaultAnimation(context)
        self.report({'INFO'}, 'Animations Imported Successfully')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_RENAME_RIG_OT_GGT(Operator):
    bl_idname = "wm_ggt.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_object
        valid = True
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
            if bpy.data.actions:
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
            self.report({'INFO'}, 'Character Bones Successfully Renamed')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_PREPARE_RIG_OT_GGT(Operator):
    bl_idname = "wm_ggt.prepare_mixamo_rig"
    bl_label = "Prepare Mixamo Rig"
    bl_description = "Fix mixamo rig to export for Godot"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_object
        visible_armature = tool.visible_armature
        valid = True
        # Apply transformations on selected Armature
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.wm_ggt.rename_mixamo_rig('EXEC_DEFAULT')

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
                    bpy.ops.scene.process_actions('EXEC_DEFAULT')
                    tool.actions.append(anim)

            self.report({'INFO'}, 'Rig Armature Prepared')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class GGT_OT_RENAME_MIXAMORIG_OT_GGT(Operator):
    bl_idname = "wm_ggt.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_object
        valid = validateArmature(self, context)
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

class GGT_OT_ARMATURE_JOIN_MESH_GGT(Operator):
    bl_idname = "wm_ggt.armature_join_mesh"
    bl_label = "Join Armature Meshes"
    bl_description = "Join every children mesh of armature into single object"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_object
        meshToJoin = None
        for mesh in target_armature.children:
            mesh.select_set(True)
            meshToJoin = mesh
        if meshToJoin:
            bpy.context.view_layer.objects.active = meshToJoin
            bpy.ops.object.join()
            bodyMesh = bpy.context.view_layer.objects.active
            bodyMesh.name = "Mesh"
            self.report({'INFO'}, 'Armature Meshes Joined')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
