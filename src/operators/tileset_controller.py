import bpy

from bpy.types import (Operator)

def fixTilePositions():
    tileSpacing = 2
    tileCollectionName = "TileCollection"
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

class TILESET_GENERATE_TILE_OT(Operator):
    bl_idname = "wm.tileset_generate_tile"
    bl_label = "Generate New Tile"
    bl_description = "Adds a new tile configuration"

    def execute(self, context):
        scene = context.scene
        tool = scene.godot_game_tools
        cam = bpy.context.scene.camera
        tileCollectionName = "TileCollection"
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
        fixTilePositions()
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
        if cam is not None:
            bpy.context.scene.render.resolution_x = 64
            bpy.context.scene.render.resolution_y = 32
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
        cam = bpy.context.scene.camera
        if cam is not None:
            bpy.context.scene.render.resolution_x = 64
            bpy.context.scene.render.resolution_y = 64
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
        if currentTile is not None:
            tileCollectionName = "TileCollection"
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
