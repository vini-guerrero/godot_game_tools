tool

extends EditorScript

var animation_tree_preset : Dictionary
var animation_tree_node_name : String = "AnimationTree"
var statemachine_name : String = "StateMachine"
var states : Array = [
	"Idle",
	"Walking",
	"Running",
	"BlendSpace",
	"Node1D"
]

func _run():
	# Prepare Export Dictionary
	animation_tree_preset["animations"] = []
	animation_tree_preset["stateTransitions"] = []
	animation_tree_preset["states"] = []
	# Get Current Scene
	var current_scene = get_editor_interface().get_edited_scene_root()
	# Get Animation Tree
	var animationTreeNode = current_scene.find_node(animation_tree_node_name, true).tree_root
	if animationTreeNode.has_node(statemachine_name):
		# Procedural StateMachine Generation
		var state_machine = animationTreeNode.get_node(statemachine_name)
		var start_node = state_machine.get_start_node()
		var end_node = state_machine.get_end_node()
		for state in range(states.size()):
			var state_name = states[state]
			var node = state_machine.get_node(state_name)
			# Treat AnimationNodeBlendSpace1D / AnimationNodeBlendSpace2D
			var children_nodes : Dictionary
			children_nodes["points_animations"] = []
			if node is AnimationNodeBlendSpace1D || node is AnimationNodeBlendSpace2D: 
				var points_count = node.get_blend_point_count()
				children_nodes["points_count"] = points_count
				for point in points_count:
					var animation_name = node.get_blend_point_node(point).animation
					var animation_position = node.get_blend_point_position(point)
					var new_animation_point = {
						"index": point,
						"animation": animation_name,
						"position": animation_position
					}
					children_nodes["points_animations"].append(new_animation_point)
			# Remove Unnecessary Props
			if node is AnimationNodeAnimation: children_nodes.erase("points_animations")
			# Export State Transitions
			var node_transition = state_machine.get_transition(state)
			var transition_to = state_machine.get_transition_to(state)
			var transition_from = state_machine.get_transition_from(state)
			var new_transition = {
				"from": transition_from,
				"switchMode": node_transition.switch_mode,
				"xFadeTime": node_transition.xfade_time,
				"to": transition_to
			}
			# Export State
			var node_position = state_machine.get_node_position(state_name)
			var is_start_node : bool
			var is_end_node : bool
			is_start_node = true if state_name == start_node else false
			is_end_node = true if state_name == end_node else false
			var new_state = {
				"name": state_name,
				"positionX": node_position.x,
				"positionY": node_position.y,
				"start": is_start_node,
				"end": is_end_node,
				"children_nodes": children_nodes,
				"type": node.get_class()
			}
			# Export Animations
			animation_tree_preset["animations"].append(state_name)
			animation_tree_preset["states"].append(new_state)
			animation_tree_preset["stateTransitions"].append(new_transition)
	
	_exportJSONFile(animation_tree_preset, "res://test.json")


func _exportJSONFile(data : Dictionary, save_path : String):
	var save_data = File.new()
	save_data.open(save_path, File.WRITE)
	save_data.store_line(to_json(data))
	save_data.close()
