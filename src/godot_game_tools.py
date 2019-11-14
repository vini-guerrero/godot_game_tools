bl_info = {
    "name": "Godot Game Tools",
    "description": "This Add-On provides features for better export options with Godot Game Engine",
    "author": "Vinicius Guerrero",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Godot Game Tools"
}

import bpy
import glob

from bpy.props import (StringProperty, PointerProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)

# ------------------------------------------------------------------------
#    Addon Scene Properties
# ------------------------------------------------------------------------

class AddonProperties(PropertyGroup):

    action_name: StringProperty(name="Animation", description="Choose the action name you want for your animation in the dopesheet", maxlen=1024)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_RENAMEMIXAMORIG(Operator):
    bl_idname = "wm.rename_mixamo_rig"
    bl_label = "Rename Rig Bones"
    bl_description = "Rename rig bones"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        actionName = tool.action_name
        bpy.ops.object.mode_set(mode = 'OBJECT')
        if not bpy.ops.object:
            self.report({'INFO'}, 'Please select the armature')
        bpy.context.object.show_in_front = True
        for rig in bpy.context.selected_objects:
            if rig.type == 'ARMATURE':
                bpy.context.object.animation_data.action.name = actionName
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
            bpy.context.scene.frame_end=bpy.context.object.animation_data.action.frame_range[-1]
        self.report({'INFO'}, 'Character Ready For Export Process')
        return {'FINISHED'}


class WM_OT_PREPAREMIXAMORIG(Operator):
    bl_idname = "wm.prepare_mixamo_rig"
    bl_label = "Prepare Mixamo Rig"
    bl_description = "Fix mixamo rig to export for Godot"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.area.ui_type = 'FCURVES'
        bpy.context.space_data.dopesheet.filter_text = "location (mixamorig:Hips)"
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.space_data.pivot_point = 'CURSOR'
        bpy.context.scene.frame_current = 0
        bpy.context.space_data.cursor_position_y = 0
        bpy.ops.transform.resize(value=(1, 0.01, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.context.area.ui_type = 'VIEW_3D'
        self.report({'INFO'}, 'Rig Armature Prepared')
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
        box.label(text="Mixamo Armature", icon='ARMATURE_DATA')
        box.prop(tool, "action_name")
        box.operator("wm.prepare_mixamo_rig", icon="ASSET_MANAGER")
        box.operator("wm.rename_mixamo_rig", icon="BONE_DATA")
        row.separator()
        row = layout.row()

# ------------------------------------------------------------------------
#    Addon Registration
# ------------------------------------------------------------------------

classes = (AddonProperties, WM_OT_PREPAREMIXAMORIG, WM_OT_RENAMEMIXAMORIG, OBJECT_PT_CustomPanel)

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
