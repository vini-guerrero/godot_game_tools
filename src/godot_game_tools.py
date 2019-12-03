bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero",
    "version": (1, 0, 3),
    "blender": (2, 81, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "tracker_url": "https://github.com/vini-guerrero/Godot_Game_Tools",
    "category": "Godot Game Tools"
}

import bpy
import glob
import os
from bpy_extras.io_utils import ImportHelper
from bl_ui.properties_object import ObjectButtonsPanel, OBJECT_PT_transform
from bpy.props import (StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)

# ------------------------------------------------------------------------
#    Development Functions
# ------------------------------------------------------------------------

def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    return area, space
    return None, None


def console_write(text):
    area, space = console_get()
    if space is None:
        return
    text = str(text)
    context = bpy.context.copy()
    context.update(dict(space=space,area=area))
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')


def populateAnimations(self, context):
    animationsArr = []
    actionNamesList = []
    if len(bpy.data.actions) > 0:
        for action in bpy.data.actions:
            actionNamesList.append(action.name)
        actionNamesList = sorted(actionNamesList)
        for action in actionNamesList:
            item = (action, action, action)
            animationsArr.append(item)
    return animationsArr


def toggleArmatureVisibility(self, context):
    scene = context.scene
    tool = scene.godot_game_tools
    target_armature = tool.target_name
    visible_armature = tool.visible_armature
    bpy.data.objects["Armature"].select_set(True)
    target_armature.hide_viewport = not visible_armature
    bpy.context.object.show_in_front = not visible_armature


def validateArmature(self, context):
    scene = context.scene
    tool = scene.godot_game_tools
    target_armature = tool.target_name
    valid = False
    if target_armature is not None:
        if target_armature.type == "ARMATURE":
            valid = True
        else:
            self.report({'INFO'}, 'Please select a valid armature')
    else:
        self.report({'INFO'}, 'Please select a valid armature')
    return valid


# ------------------------------------------------------------------------
#    Addon Scene Properties
# ------------------------------------------------------------------------

class AddonProperties(PropertyGroup):

    action_name: StringProperty(name="New Name", description="Choose the action name you want to rename your animation in the dopesheet", maxlen=1024)
    rootmotion_name: StringProperty(name="Rootmotion Name", description="Choose name you want for the RootMotion Bone", maxlen=1024, default="RootMotion")
    target_name: PointerProperty(name="Target", description="Select the target armature you want the animations to be merged into", type=bpy.types.Object)
    animations: EnumProperty(name="Animations", description="Available armature animations", items=populateAnimations, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    visible_armature: BoolProperty(name="Show Armature Bones", description="Hides / Show armature bones once animations are loaded", default=True, update=toggleArmatureVisibility)
    rootmotion_all: BoolProperty(name="Apply Rootmotion To All Animations", description="Choose to apply rootmotion to all animations or current only", default=True, update=None)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------


class ANIMATION_PLAYER_OT(Operator):
    bl_idname = "wm.animation_player"
    bl_label = "Play Animation"
    bl_description = "Play armature animations"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        bpy.context.scene.frame_start = 2
        valid = validateArmature(self, context)
        if valid:
            if len(bpy.data.actions) > 0:
                animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                animationIndex = bpy.data.actions.keys().index(animation)
                target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                bpy.ops.screen.animation_play()
            self.report({'INFO'}, 'Playing Animation')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class STOP_ANIMATION_OT(Operator):
    bl_idname = "wm.animation_stop"
    bl_label = "Stop Animation"
    bl_description = "Stops curent animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        valid = validateArmature(self, context)
        if valid:
            bpy.context.scene.frame_current = 0
            bpy.ops.screen.animation_cancel()
            self.report({'INFO'}, 'Animation Stopped')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class NLA_TRACKS_OT(Operator):
    bl_idname = "wm.push_nlas"
    bl_label = "Create NLA Tracks"
    bl_description = "Push All Animations to NLA Tracks"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.ops.screen.animation_cancel()
        bpy.context.view_layer.objects.active = target_armature
        bpy.context.scene.frame_start = 2
        valid = validateArmature(self, context)
        if valid:
            if len(bpy.data.actions) > 0:
                for action in bpy.data.actions:
                    animation = action.name
                    animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
                    animationIndex = bpy.data.actions.keys().index(animation)
                    target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
                    bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
                    bpy.context.area.ui_type = 'NLA_EDITOR'
                    bpy.ops.nla.action_pushdown(channel_index=1)
            bpy.context.area.ui_type = 'VIEW_3D'
            self.report({'INFO'}, 'NLA Tracks Generated')
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class ADD_ROOTBONE_OT(Operator):
    bl_idname = "wm.add_rootbone"
    bl_label = "Add Root Bone"
    bl_description = "Adds armature root bone for root motion"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
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
                    scene.frame_set(1)
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
        target_armature = tool.target_name
        rootMotionBoneName = tool.rootmotion_name
        rootmotion_all = tool.rootmotion_all
        animationsForRootMotion = []
        valid = validateArmature(self, context)
        if valid:
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
                bpy.ops.object.mode_set(mode='OBJECT')
                self.report({'INFO'}, 'Root Motion Added')
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
        valid = validateArmature(self, context)
        if valid:
            if len(bpy.data.actions) > 0:
                bpy.context.object.animation_data.action.name = actionName
            self.report({'INFO'}, 'Animation Renamed')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

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
    bl_label = "Join Mixamo Animations"
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
        valid = validateArmature(self, context)
        if valid:
            bpy.context.object.animation_data.action.name = "T-Pose"
            self.importModels(path, target_armature, context)
            self.setDefaultAnimation(context)
            self.report({'INFO'}, 'Animations Imported Successfully')
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panels
# ------------------------------------------------------------------------

class OBJECT_PT_BVH_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.bvh_utilities_panel"
    bl_label = "BVH Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    bl_options = {"DEFAULT_CLOSED"}
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Work-In-Progress", icon='SCENE')

class OBJECT_PT_MIXAMO_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.mixamo_utilities_panel"
    bl_label = "Mixamo Utilies"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.main_panel"
    def draw(self, context):
        pass

class OBJECT_PT_ARMATURE_UTILITIES(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.armature_panel"
    bl_label = "Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Armature Setup", icon='ARMATURE_DATA')
        # box.prop(tool, "target_name")
        box.operator("wm.init_character", icon="IMPORT")
        box.operator("wm.join_animations", icon="ASSET_MANAGER")
        # box.operator("wm.prepare_mixamo_rig", icon="ASSET_MANAGER")
        box.separator()

class OBJECT_PT_ROOT_MOTION(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.rootmotion_panel"
    bl_label = "Root Motion"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Root Motion Setup", icon='ANIM_DATA')
        box.prop(tool, "visible_armature")
        box.prop(tool, "rootmotion_all")
        box.operator("wm.add_rootmotion", icon="BONE_DATA")
        box.separator()

class OBJECT_PT_ANIMATIONS(bpy.types.Panel, ObjectButtonsPanel):
    bl_idname = "object.animations_panel"
    bl_label = "Animations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_parent_id = "object.mixamo_utilities_panel"
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        tool = scene.godot_game_tools
        box = layout.box()
        box.label(text="Animations Settings", icon='SCENE')
        box.prop(tool, "animations")
        box.operator("wm.animation_player", icon="PLAY")
        box.operator("wm.animation_stop", icon="PAUSE")
        box.prop(tool, "action_name")
        box.operator("wm.rename_animation", icon="ARMATURE_DATA")
        box.operator("wm.push_nlas", icon="ANIM_DATA")
        box.separator()

class OBJECT_PT_ADDON_PANEL(Panel):
    bl_idname = "object.main_panel"
    bl_label = "Godot Game Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Godot Game Tools"
    bl_context = "objectmode"
    def draw(self, context): pass

# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------

classes = (
    AddonProperties,
    OBJECT_PT_ADDON_PANEL,
    OBJECT_PT_MIXAMO_UTILITIES,
    OBJECT_PT_BVH_UTILITIES,
    OBJECT_PT_ARMATURE_UTILITIES,
    OBJECT_PT_ROOT_MOTION,
    OBJECT_PT_ANIMATIONS,
    INIT_CHARACTER_OT,
    JOIN_ANIMATIONS_OT,
    ANIMATION_PLAYER_OT,
    STOP_ANIMATION_OT,
    NLA_TRACKS_OT,
    RENAME_ANIMATION_OT,
    ADD_ROOTBONE_OT,
    ADD_ROOTMOTION_OT
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.godot_game_tools = PointerProperty(type=AddonProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.godot_game_tools

if __name__ == "__main__":
    register()
