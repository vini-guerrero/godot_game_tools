import bpy

from bpy.types import (Operator)

class BAKE_TEXTURE_OT(bpy.types.Operator):
    bl_idname = "wm.bake_texture"
    bl_label = "Bake Texture"
    bl_description = "Bakes Selected Texture"

    def execute(self, context):
        # Validate Mesh With Material Is Selected
        bpy.context.scene.render.engine = 'CYCLES'
        activeObj = bpy.context.view_layer.objects.active
        bake_type = context.scene.cycles.bake_type
        bpy.ops.object.bake('INVOKE_DEFAULT',type = bake_type)
        self.report({'INFO'}, 'Bake Process Started')
        return {'FINISHED'}

class SAVE_BAKE_TEXTURES_OT(Operator):
    bl_idname = "wm.save_bake_textures"
    bl_label = "Save Bake Textures"
    bl_description = "Create texture for proper bake"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        animation = tool.animations
        target_armature = tool.target_name
        actionName = tool.action_name
        activeObj = bpy.context.view_layer.objects.active
        if len(activeObj.material_slots) > 0:
            activeObj = bpy.context.view_layer.objects.active
            slot = activeObj.material_slots[0]
            material = slot.material
            nodes = material.node_tree.nodes
            nodeIndex = 0
            for node in nodes:
                if node.bl_idname == "ShaderNodeTexImage":
                    imgName = "bake"+ str(nodeIndex) + ".png"
                    node.image.filepath = "//" + imgName
                    node.image.save()
                    nodeIndex += 1
            self.report({'INFO'}, 'Bake Textures Saved')
        return {'FINISHED'}
