bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero",
    "version": (1, 0, 2),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Godot Game Tools"
}

import bpy
import glob
import os

from bpy_extras.io_utils import ImportHelper
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


# ------------------------------------------------------------------------
#    Addon Scene Properties
# ------------------------------------------------------------------------

class AddonProperties(PropertyGroup):

    action_name: StringProperty(name="Animation", description="Choose the action name you want to rename your animation in the dopesheet", maxlen=1024)
    rootmotion_name: StringProperty(name="Rootmotion Name", description="Choose name you want for the RootMotion Bone", maxlen=1024, default="RootMotion")
    target_name: PointerProperty(name="Target", description="Select the target armature you want the animations to be merged into", type=bpy.types.Object)
    animations: EnumProperty(name="Animations", description="Available armature animations", items=populateAnimations, default=None, options={'ANIMATABLE'}, update=None, get=None, set=None)
    visible_armature: BoolProperty(name="Show Armature Bones", description="Hides / Show armature bones once animations are loaded", default=True, update=toggleArmatureVisibility)
    rootmotion_all: BoolProperty(name="Apply Rootmotion To All Animations", description="Choose to apply rootmotion to all animations or current only", default=True, update=None)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_RENAME_MIXAMORIG(Operator):
    bl_idname = "wm.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        visible_armature = tool.visible_armature
        target_armature = tool.target_name
        bpy.data.objects["Armature"].select_set(True)
        target_armature.hide_viewport = False
        bpy.ops.object.mode_set(mode='OBJECT')
        if not bpy.ops.object:
            self.report({'INFO'}, 'Please select the armature')
        for rig in bpy.context.selected_objects:
            if rig.type == 'ARMATURE':
                for mesh in rig.children:
                    for vg in mesh.vertex_groups:
                        new_name = vg.name
                        new_name = new_name.replace("mixamorig:","")
                        rig.pose.bones[vg.name].name = new_name
                        vg.name = new_name
                for bone in rig.pose.bones:
                    bone.name = bone.name.replace("mixamorig:","")
        for action in bpy.data.actions:
            fc = action.fcurves
            for f in fc:
                f.data_path = f.data_path.replace("mixamorig:","")
        if bpy.data.actions:
            bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
        self.report({'INFO'}, 'Character Bones Successfully Renamed')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class WM_OT_PREPARE_MIXAMORIG(Operator):
    bl_idname = "wm.prepare_mixamo_rig"
    bl_label = "Prepare Mixamo Rig"
    bl_description = "Fix mixamo rig to export for Godot"

    def mixamoRigFixer(self, context):
        filter1 = "location (mixamorig:Hips)"
        filter2 = "Location (Hips)"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.area.ui_type = 'FCURVES'
        bpy.context.space_data.dopesheet.filter_text = filter1
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.space_data.pivot_point = 'CURSOR'
        bpy.context.scene.frame_current = 0
        bpy.context.space_data.cursor_position_y = 0
        bpy.ops.transform.resize(value=(1, 0.01, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.context.space_data.dopesheet.filter_text = filter2
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.space_data.pivot_point = 'CURSOR'
        bpy.context.scene.frame_current = 0
        bpy.context.space_data.cursor_position_y = 0
        bpy.ops.transform.resize(value=(1, 0.01, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.context.area.ui_type = 'VIEW_3D'

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        target_armature = tool.target_name
        visible_armature = tool.visible_armature
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
                self.mixamoRigFixer(context)
        self.report({'INFO'}, 'Rig Armature Prepared')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class WM_OT_ANIMATION_PLAYER(Operator):
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
        bpy.context.scene.frame_start = 0
        if len(bpy.data.actions) > 0:
            animationToPlay = [anim for anim in bpy.data.actions.keys() if anim in (animation)]
            animationIndex = bpy.data.actions.keys().index(animation)
            target_armature.animation_data.action = bpy.data.actions.values()[animationIndex]
            bpy.context.scene.frame_end = bpy.context.object.animation_data.action.frame_range[-1]
            bpy.ops.screen.animation_play()
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class WM_OT_STOP_ANIMATION(Operator):
    bl_idname = "wm.animation_stop"
    bl_label = "Stop Animation"
    bl_description = "Stops curent animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        bpy.context.scene.frame_current = 0
        bpy.ops.screen.animation_cancel()
        return {'FINISHED'}


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class WM_OT_ADD_ROOTBONE(Operator):
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

class WM_OT_ADD_ROOTMOTION(Operator):
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
        # Call Operator From Outside Class
        animationsForRootMotion = []
        if rootmotion_all:
            for action in bpy.data.actions: animationsForRootMotion.append(action)
        else:
            animationsForRootMotion.append(bpy.context.object.animation_data.action)
        bpy.ops.wm.add_rootbone()
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

class WM_OT_RENAME_ANIMATION(Operator):
    bl_idname = "wm.rename_animation"
    bl_label = "Rename Current Animation"
    bl_description = "Renames current animation"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        actionName = tool.action_name
        if len(bpy.data.actions) > 0:
            bpy.context.object.animation_data.action.name = actionName
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class WM_OT_JOIN_ANIMATIONS(Operator, ImportHelper):
    bl_idname = "wm.join_animations"
    bl_label = "Join Mixamo Animations"
    bl_description = "Join mixamo animations into a single armature"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".fbx"
    filter_glob = StringProperty(default="*.fbx", options={'HIDDEN'})
    files = CollectionProperty(type=bpy.types.PropertyGroup)

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
                            obj.name = fileNamesList[index]
                            obj.animation_data.action.name = fileNamesList[index]
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
        if target_armature is not None:
            if target_armature.type == 'ARMATURE':
                bpy.context.object.animation_data.action.name = "T-Pose"
            else:
                self.report({'INFO'}, 'Please select the armature')
            self.importModels(path, target_armature, context)
            self.setDefaultAnimation(context)
        else:
            self.report({'INFO'}, 'Please select a valid armature')
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_idname = "object.custom_panel"
    bl_label = "Godot Game Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Godot Game Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool = scene.godot_game_tools

        # Render Settings
        row = layout.row()
        box = layout.box()
        box.label(text="Mixamo Utilities", icon='ARMATURE_DATA')
        box.prop(tool, "target_name")
        box.operator("wm.join_animations", icon="IMPORT")
        box.operator("wm.prepare_mixamo_rig", icon="ASSET_MANAGER")
        box.operator("wm.rename_mixamo_rig", icon="BONE_DATA")
        # box.operator("wm.add_rootbone", icon="BONE_DATA")
        box.prop(tool, "rootmotion_name")
        box.prop(tool, "visible_armature")
        box.prop(tool, "rootmotion_all")
        box.operator("wm.add_rootmotion", icon="ANIM_DATA")
        box.separator()
        box.prop(tool, "animations")
        box.operator("wm.animation_player", icon="SCENE")
        box.operator("wm.animation_stop", icon="SCENE")
        box.prop(tool, "action_name")
        box.operator("wm.rename_animation", icon="ARMATURE_DATA")
        row.separator()
        row = layout.row()

# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------

classes = (
    AddonProperties,
    WM_OT_PREPARE_MIXAMORIG,
    WM_OT_RENAME_MIXAMORIG,
    WM_OT_JOIN_ANIMATIONS,
    WM_OT_ANIMATION_PLAYER,
    WM_OT_STOP_ANIMATION,
    WM_OT_RENAME_ANIMATION,
    WM_OT_ADD_ROOTBONE,
    WM_OT_ADD_ROOTMOTION,
    OBJECT_PT_CustomPanel
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
