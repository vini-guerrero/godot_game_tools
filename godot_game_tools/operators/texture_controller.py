import bpy
import os
import glob

from bpy.types import (Operator)

class BAKE_TEXTURE_OT(bpy.types.Operator):
    bl_idname = "wm_ggt.bake_texture"
    bl_label = "Bake Texture"
    bl_description = "Bakes Selected Texture"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        textureSize = tool.bake_texture_size
        bakeFilter = tool.bake_filter
        bake_texture_path = tool.bake_texture_path
        bake_texture_name = tool.bake_texture_name
        texturePath = bpy.path.abspath(bake_texture_path)
        fileName = os.path.join(texturePath, bake_texture_name + ".png")
        currentEngine = bpy.context.scene.render.engine
        activeObj = bpy.context.view_layer.objects.active
        # Validate Mesh With Material Is Selected
        mesh = None
        if activeObj is not None:
            if activeObj.type == "MESH":
                mesh = activeObj
            if activeObj.type == "ARMATURE":
                if len(activeObj.children) > 0:
                    mesh = activeObj.children[0]
        if mesh is not None:
            if len(mesh.material_slots) > 0:
                # Bake
                bpy.context.view_layer.objects.active = mesh
                bpy.context.scene.render.engine = 'CYCLES'
                bake_type = context.scene.cycles.bake_type
                bpy.ops.object.bake('INVOKE_DEFAULT', save_mode='EXTERNAL', type=bake_type, width=textureSize, height=textureSize, filepath=fileName, margin=16)
                # bpy.context.scene.render.engine = currentEngine
                self.report({'INFO'}, 'Bake Process Started')
            else:
                self.report({'INFO'}, 'Please select a valid mesh containing materials to bake the texture')
        else:
                self.report({'INFO'}, 'Please select a valid mesh to bake the texture')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class CREATE_BAKE_TEXTURES_OT(Operator):
    bl_idname = "wm_ggt.create_bake_texture"
    bl_label = "Create Bake Texture"
    bl_description = "Create texture for proper bake"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        textureSize = tool.bake_texture_size
        bake_texture_name = tool.bake_texture_name
        activeObj = bpy.context.view_layer.objects.active
        mesh = None
        if activeObj is not None:
            if activeObj.type == "MESH":
                mesh = activeObj
            if activeObj.type == "ARMATURE":
                if len(activeObj.children) > 0:
                    mesh = activeObj.children[0]
        if mesh is not None:
            if len(mesh.material_slots) > 0:
                slot = mesh.material_slots[0]
                material = slot.material
                nodes = material.node_tree.nodes
                links = material.node_tree.links
                # for link in links:
                #     if link.from_node.bl_idname == "ShaderNodeTexImage": material.node_tree.links.remove(link)
                # Create New Image for Baking
                bakeTexture = nodes.new(type='ShaderNodeTexImage')
                bakeTexture.location = 600,300
                bakeImage = bpy.data.images.new(bake_texture_name, width=textureSize, height=textureSize)
                bakeImage.file_format = "PNG"
                bakeImage.source = "GENERATED"
                bakeTexture.image = bakeImage
                bakeTexture.select = True
                material.node_tree.nodes.active = bakeTexture
            self.report({'INFO'}, 'Bake Texture Created')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class SAVE_BAKE_TEXTURES_OT(Operator):
    bl_idname = "wm_ggt.save_bake_textures"
    bl_label = "Save Current Texture"
    bl_description = "Saves current active textures"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        bake_texture_path = tool.bake_texture_path
        bake_texture_name = tool.bake_texture_name
        texturePath = bpy.path.abspath(bake_texture_path)
        activeObj = bpy.context.view_layer.objects.active
        if len(activeObj.material_slots) > 0:
            bakedImage = bpy.data.images[bake_texture_name]
            fileName = os.path.join(texturePath, bake_texture_name + ".png")
            bakedImage.filepath = fileName
            bakedImage.save()
            self.report({'INFO'}, 'Bake Textures Saved')
        return {'FINISHED'}
