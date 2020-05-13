tool
extends EditorPlugin

const containerPath = "res://addons/godot_game_tools/views/GGT.tscn"
const dockScn = preload(containerPath)
var dock : ScrollContainer

func _enter_tree():
	dock = dockScn.instance()
	add_control_to_dock(DOCK_SLOT_RIGHT_UL, dock)

func _exit_tree():
	remove_control_from_docks(dock)
	dock.free()
