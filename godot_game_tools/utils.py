import bpy
from bpy.props import (IntProperty, StringProperty, PointerProperty, CollectionProperty, EnumProperty, BoolProperty)
from bpy.types import (PropertyGroup)


def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    return area, space
    return None, None

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def console_write(text):
    area, space = console_get()
    if space is None:
        return
    text = str(text)
    context = bpy.context.copy()
    context.update(dict(space=space,area=area))
    for line in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=line, type='OUTPUT')


# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

def validateArmature():
    context = bpy.context
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

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

