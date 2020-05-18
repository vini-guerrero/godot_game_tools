tool

extends EditorScript

var animation_tree_preset : Dictionary
var animation_tree_node_name : String = "AnimationTree"
var statemachine_name : String = "StateMachine"

func _run(): prints(_generateAnimationTreeExport())


func _generateAnimationTreeExport() -> Dictionary:
	# Animation States 
	var data = _getAnimationStatesAndTransitions()
	var states = data["animation_states"]
	# Prepare Export Dictionary
	var animation_tree_preset : Dictionary
	animation_tree_preset["animations"] = []
	animation_tree_preset["states_transitions"] = data["states_transitions"]
	animation_tree_preset["states"] = []
	# Get Current Scene
	var current_scene = _getCurrentScene()
	# Get Animation Tree
	var animationTreeNode = current_scene.find_node(animation_tree_node_name, true).tree_root
	if animationTreeNode.has_node(statemachine_name):
		# Procedural StateMachine Generation
		var state_machine = animationTreeNode.get_node(statemachine_name)
		var start_node = state_machine.get_start_node()
		var end_node = state_machine.get_end_node()
		var transition_amount = state_machine.get_transition_count()
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
					var new_animation_point = { "index": point, "animation": animation_name }
					# Blend Position (Float) or (Vector2)
					if node is AnimationNodeBlendSpace1D: 
						new_animation_point["position"] = animation_position
					if node is AnimationNodeBlendSpace2D:
						new_animation_point["position_x"] = animation_position.x
						new_animation_point["position_y"] = animation_position.y
					children_nodes["points_animations"].append(new_animation_point)
			# Remove Unnecessary Props
			if node is AnimationNodeAnimation: children_nodes.erase("points_animations")
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
			animation_tree_preset["transition_amount"] = transition_amount
			animation_tree_preset["preset_name"] = "Sample Preset"
			animation_tree_preset["preset_creator"] = "Sample Author"
			animation_tree_preset["preset_version"] = "1.0"
			animation_tree_preset["rootmotion_bone"] = "Rootmotion"
			animation_tree_preset["state_machine_node"] = statemachine_name
			animation_tree_preset["preset_creation_date"] = str(_getDatetime())
	return animation_tree_preset


func _getAnimationStatesAndTransitions() -> Dictionary:
	# Get States
	var animation_data : Dictionary
	animation_data["animation_states"] = []
	animation_data["states_transitions"] = []
	# Get Current Scene
	var current_scene = _getCurrentScene()
	# Get Animation Tree
	var animationTreeNode = current_scene.find_node(animation_tree_node_name, true).tree_root
	if animationTreeNode.has_node(statemachine_name):
		# Procedural StateMachine Generation
		var state_machine = animationTreeNode.get_node(statemachine_name)
		var transition_amount = state_machine.get_transition_count()
		for t in transition_amount:
			var node_transition = state_machine.get_transition(t)
			var transition_to = state_machine.get_transition_to(t)
			var transition_from = state_machine.get_transition_from(t)
			if not animation_data["animation_states"].has(transition_to): 
				animation_data["animation_states"].append(transition_to)
			if not animation_data["animation_states"].has(transition_from): 
				animation_data["animation_states"].append(transition_from)
			var new_transition = {
				"from": transition_from,
				"switchMode": node_transition.switch_mode,
				"xFadeTime": node_transition.xfade_time,
				"to": transition_to
			}
			animation_data["states_transitions"].append(new_transition)
	return animation_data


func _getDatetime() -> String:
	var date_time : String
	var current_time = OS.get_time()
	var hour = str(current_time.hour)
	var minute = str(current_time.minute)
	var seconds = str(current_time.second)
	var current_date = OS.get_datetime()
	var year = str(current_date.year)
	var month = str(current_date.month)
	var day = str(current_date.day)
	date_time = day + "/" + month + "/" + year
	date_time += " " + hour + ":" + minute + ":" + seconds
	return date_time


func _getCurrentScene() -> Node: return get_editor_interface().get_edited_scene_root()
