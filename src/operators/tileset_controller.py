import bpy
import os
from pathlib import Path

from bpy.types import (Operator)

def fixTilePositions(tileCollectionName):
    tileSpacing = 2
    tileCollection = bpy.data.collections.get(tileCollectionName)
    tilesInCollection = tileCollection.objects
    if len(tilesInCollection) > 0:
        firstTile = tilesInCollection[0]
        firstTilePosition = firstTile.location
        tileSize = firstTile.dimensions.x
        previousTilePosition = None
        tileIndex = 0
        if len(tilesInCollection) > 1:
            # Reset Tile Positions
            for tile in tilesInCollection: tile.location = firstTilePosition
            for tile in tilesInCollection:
                if tileIndex == 0:
                    pass
                else:
                    if previousTilePosition is not None: tile.location = previousTilePosition
                    tile.location.x += tileSize + tileSpacing
                    previousTilePosition = tile.location
                tileIndex +=1

def writeToFile(variable, content, lineBreakAmount = None):
    variable += content
    if lineBreakAmount == None:
      variable += '\n'
    else:
      for index in range(0, lineBreakAmount):
        variable += '\n'
    return variable


class TILESET_GENERATE_TILE_OT(Operator):
    bl_idname = "wm.tileset_generate_tile"
    bl_label = "Generate New Tile"
    bl_description = "Adds a new tile configuration"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        cam = bpy.context.scene.camera
        tileCollectionName = tool.tile_collection_name
        if bpy.data.collections.get(tileCollectionName) is None:
          tileCollection = bpy.data.collections.new(tileCollectionName)
          bpy.context.scene.collection.children.link(tileCollection)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, 0))
        tileCollection = bpy.data.collections.get(tileCollectionName)
        newTile = bpy.context.view_layer.objects.active
        newTile.name = "Tile"
        bpy.context.scene.collection.children[0].objects.unlink(newTile)
        tileCollection.objects.link(newTile)
        fixTilePositions(tileCollectionName)
        if cam is not None: bpy.ops.view3d.camera_to_view_selected()
        self.report({'INFO'}, 'New Tile Added')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class TILESET_SET_ISOMETRIC_CAMERA_OT(Operator):
    bl_idname = "wm.tileset_set_isometric_camera"
    bl_label = "Set Isometric Camera"
    bl_description = "Sets active camera to isometric projection for tiles rendering"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        cam = bpy.context.scene.camera
        tileset_tile_width = tool.tileset_tile_width
        tileset_tile_height = tool.tileset_tile_height
        if cam is not None:
            bpy.context.scene.render.resolution_x = tileset_tile_width
            bpy.context.scene.render.resolution_y = tileset_tile_height
            bpy.context.scene.render.film_transparent = True
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = 2.84
            cam.location[0] = 10
            cam.location[1] = -10
            cam.location[2] = 8.17
            cam.rotation_euler[0] = 1.0472
            cam.rotation_euler[2] = 0.785398
            self.report({'INFO'}, 'Isometric Camera Set')
        else:
            self.report({'INFO'}, 'No Active Camera Found')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class TILESET_SET_TOPDOWN_CAMERA_OT(Operator):
    bl_idname = "wm.tileset_set_topdown_camera"
    bl_label = "Set Top-Down Camera"
    bl_description = "Sets active camera to top-down projection for tiles rendering"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        tileset_tile_width = tool.tileset_tile_width
        tileset_tile_height = tool.tileset_tile_height
        cam = bpy.context.scene.camera
        if cam is not None:
            bpy.context.scene.render.resolution_x = tileset_tile_width
            bpy.context.scene.render.resolution_y = tileset_tile_height
            bpy.context.scene.render.film_transparent = True
            cam.data.type = 'ORTHO'
            cam.data.ortho_scale = 2
            cam.location[0] = 0
            cam.location[1] = 0
            cam.location[2] = 1
            cam.rotation_euler[0] = 0
            cam.rotation_euler[1] = -0
            cam.rotation_euler[2] = 0
            self.report({'INFO'}, 'Top-Down Camera Set')
        else:
            self.report({'INFO'}, 'No Active Camera Found')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class TILESET_MOVE_CAMERA_TILE_OT(Operator):
    bl_idname = "wm.tileset_move_camera_tile"
    bl_label = "Move Camera Next Tile"
    bl_description = "Moves the active camera towards next tile"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        currentTile = bpy.context.view_layer.objects.active
        tileCollectionName = tool.tile_collection_name
        if currentTile is not None:
            tileCollection = bpy.data.collections.get(tileCollectionName)
            tilesInCollection = tileCollection.objects
            tileIndex = 0
            matchIndex = None
            if len(tilesInCollection) > 1:
                for tile in tilesInCollection:
                    if tile == currentTile and matchIndex is None: matchIndex = tileIndex
                    tileIndex += 1
            if len(tilesInCollection) > matchIndex + 1:
                nextTile = tilesInCollection[matchIndex + 1]
            else:
                nextTile = tilesInCollection[0]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = nextTile
            nextTile.select_set(True)
            bpy.ops.view3d.camera_to_view_selected()
            self.report({'INFO'}, 'Next Tile Camera Set')
        else:
            self.report({'INFO'}, 'Select A Valid Collection Tile Before Switching')
        return {'FINISHED'}

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #

class TILESET_EXPORT_GODOT_TILESET_OT(Operator):
    bl_idname = "wm.tileset_export_godot_tileset"
    bl_label = "Export Godot Tileset"
    bl_description = "Exports a resource file and scene containing configurations for Godot Engine"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        tileset_generate_path = tool.tileset_generate_path
        tileCollectionName = tool.tile_collection_name
        tileset_tile_width = tool.tileset_tile_width
        tileset_tile_height = tool.tileset_tile_height
        currentTile = bpy.context.view_layer.objects.active
        if tileset_generate_path is not None:
            tileCollection = bpy.data.collections.get(tileCollectionName)
            tilesInCollection = tileCollection.objects
            totalTiles = len(tilesInCollection)
            if totalTiles > 0 and tool.tileset_generate_path is not None:
                assetPath = "res://" + str(tool.tileset_generate_path.split(os.path.sep)[-2]) + "/"

                # .TSCN Godot File
                tilesetTscnFileName = "Tileset.tscn"
                fileNameTscn = os.path.join(tileset_generate_path, tilesetTscnFileName)
                fileTscn = open(fileNameTscn, "w+")
                # File Header
                fileHeaderTscn = ''
                fileHeaderTscn = writeToFile(fileHeaderTscn, '[gd_scene load_steps=2 format=2]', 2)

                # Gather Tiles in Collection
                headerTscnIndex = 0
                for tile in tilesInCollection:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = tile
                    tile.select_set(True)
                    bpy.ops.view3d.camera_to_view_selected()
                    # Render Tiles
                    filepath = bpy.data.filepath
                    directory = os.path.dirname(filepath)
                    file = os.path.join(tileset_generate_path, tile.name)
                    bpy.context.scene.render.filepath = file
                    bpy.ops.render.render(animation=False, write_still=True)
                    resourceDirectory = str(Path(file).parents[0])
                    if headerTscnIndex == totalTiles -1:
                        fileHeaderTscn = writeToFile(fileHeaderTscn, '[ext_resource path="' + assetPath +  str(tile.name) + '.png" type="Texture" id=' + str(headerTscnIndex) + ']', 2)
                    else:
                        fileHeaderTscn = writeToFile(fileHeaderTscn, '[ext_resource path="' + assetPath +  str(tile.name) + '.png" type="Texture" id=' + str(headerTscnIndex) + ']')
                    headerTscnIndex += 1

                fileHeaderTscn = writeToFile(fileHeaderTscn, '[node name="Tileset" type="Node2D"]', 2)

                # File Content
                fileContentTscn = ''
                contentTscnIndex = 0
                for tile in tilesInCollection:
                    if contentTscnIndex > 0:
                        tilePositionX = tileset_tile_width * contentTscnIndex
                        tilePositionY = 0
                    else:
                        tilePositionX = 0
                        tilePositionY = 0

                    fileContentTscn = writeToFile(fileContentTscn, '[node name="' + str (tile.name) + '" type="Sprite" parent="."]')
                    fileContentTscn = writeToFile(fileContentTscn, 'position = Vector2( ' + str(tilePositionX) + ', ' + str(tilePositionY) + ' )')
                    fileContentTscn = writeToFile(fileContentTscn, 'texture = ExtResource( ' + str(contentTscnIndex) + ' )', 1)
                    contentTscnIndex += 1

                # File to Disk
                fileTscn.write(fileHeaderTscn)
                fileTscn.write(fileContentTscn)
                fileTscn.close()


                # .TRES Godot File
                tilesetTresFileName = "tileset.tres"
                fileNameTres = os.path.join(tileset_generate_path, tilesetTresFileName)
                fileTres = open(fileNameTres, "w+")
                # File Header
                fileHeaderTres = ''
                fileHeaderTres = writeToFile(fileHeaderTres, '[gd_resource type="TileSet" load_steps=2 format=2]', 2)

                tileTresIndex = 0
                for tile in tilesInCollection:
                    lineBreak = 1
                    if tileTresIndex == totalTiles -1: lineBreak = 2
                    fileHeaderTres = writeToFile(fileHeaderTres, '[ext_resource path="' + assetPath +  str(tile.name) + '.png" type="Texture" id=' + str(tileTresIndex) + ']', lineBreak)
                    tileTresIndex += 1
                fileHeaderTres = writeToFile(fileHeaderTres, '[resource]')

                # File Content
                fileContentTres = ''
                contentTresIndex = 0
                for tile in tilesInCollection:
                    # File Content
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/name = "' + str (tile.name) + '"')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/texture = ExtResource( 1 )')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/tex_offset = Vector2( 0, 0 )')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/region = Rect2( 0, 0, ' + str(tileset_tile_width) + ', ' + str(tileset_tile_height) + ' )')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/tile_mode = 0')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/occluder_offset = Vector2( ' + str(tileset_tile_width) + ', ' + str(tileset_tile_height) + ' )')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/navigation_offset = Vector2( ' + str(tileset_tile_width) + ', ' + str(tileset_tile_height) + ' )')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/shapes = [  ]')
                    fileContentTres = writeToFile(fileContentTres, str(contentTresIndex) + '/z_index = 0', 2)
                    contentTresIndex += 1

                # File to Disk
                fileTres.write(fileHeaderTres)
                fileTres.write(fileContentTres)
                fileTres.close()


                self.report({'INFO'}, 'Godot Engine Tileset Resource File Exported')
        else:
            self.report({'INFO'}, 'Please select a destination folder for the file export')
        return {'FINISHED'}
