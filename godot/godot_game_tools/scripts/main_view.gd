tool 

extends ScrollContainer

onready var load_file_btn = $HBoxContainer/VBoxContainer/SelectCharFileBtn
onready var armature_setup_btn = $HBoxContainer/VBoxContainer/ArmatureSetupBtn
onready var statemachine_setup_btn = $HBoxContainer/VBoxContainer/StateMachineSetupBtn
onready var load_file = $HBoxContainer/VBoxContainer/CharFilePath/LoadFileDialog
onready var load_file_label = $HBoxContainer/VBoxContainer/CharFilePath/PathField
onready var armature_collision_toggle = $HBoxContainer/VBoxContainer/ArmatureSettings/CollisionShapeToggle
onready var armature_rootmotion_view_toggle = $HBoxContainer/VBoxContainer/ArmatureSettings/RootMotionToggle


var popup_window_size : Vector2 = Vector2(1000, 1000)
var character_file : Dictionary
var animation_tree_node_name : String = "AnimationTree"
var armature_collision : bool = false
var armature_rootmotion_view : bool = false


func _ready():
	armature_collision_toggle.connect("toggled", self, "_toggleArmatureCollision")
	armature_rootmotion_view_toggle.connect("toggled", self, "_toggleArmatureRootMotionView")
	statemachine_setup_btn.connect("button_down", self, "_stateMachineSetup")
	armature_setup_btn.connect("button_down", self, "_armatureSetup")
	load_file_btn.connect("button_down", self, "_loadCharFile")
	load_file.connect("file_selected", self, "_fileSelected")


func _armatureSetup():
	if not character_file.empty():
		var current_scene = _getCurrentScene()
		var root_motion_bone = character_file.rootMotionBone
		var state_machine_name = character_file.nodeName
		_addArmatureBasicSetup(current_scene, root_motion_bone, state_machine_name)


func _stateMachineSetup():
	if not character_file.empty():
		var current_scene = _getCurrentScene()
		_addStateMachine(current_scene, character_file)


func _fileSelected(_filePath : String):
	load_file_label.text = str(_filePath)
	var charfile_content = _readJsonData(_filePath)
	var current_scene = _getCurrentScene()
	if charfile_content: character_file = charfile_content


func _readJsonData(filePath):
	var file = File.new()
	file.open(filePath, file.READ)
	var json = JSON.parse(file.get_as_text())
	file.close()
	return json.result


func _toggleArmatureCollision(new_value : bool): armature_collision = new_value
func _toggleArmatureRootMotionView(new_value : bool): armature_rootmotion_view = new_value
func _loadCharFile(): load_file.popup_centered_minsize(popup_window_size)
func _getCurrentScene(): return get_tree().get_edited_scene_root()


func _addArmatureBasicSetup(current_scene, rootmotion_bone, statemachine_name):
	if current_scene:
		# Script Variables
#		var armatureSkeleton = "Armature/Skeleton:"
#		var armaturePath = str(armatureSkeleton) + str(rootmotion_bone)
#		var rootMotionTrackPath = armaturePath
		var animationPlayerPath = current_scene.find_node("AnimationPlayer", true).get_path()
		var animationNodeName : String = str(statemachine_name)
		var animationNodePosition : Vector2 =  Vector2(40, 80)
		var outputNodePosition : Vector2 =  Vector2(400, 80)
		var outputNode : String = "output"
		var blendTree : AnimationNodeBlendTree
		var stateMachine : AnimationNodeStateMachine
		var animationTree : AnimationTree
		var rootMotionView: RootMotionView
		var characterCollision : CollisionShape
		var characterCollisionCapsule : CapsuleShape
		
		# Collision Shape
		if armature_collision:
			characterCollision = CollisionShape.new()
			characterCollisionCapsule = CapsuleShape.new()
			characterCollisionCapsule.radius = 0.5
			characterCollision.set_shape(characterCollisionCapsule)
			characterCollision.rotation_degrees.x = 90
			characterCollision.translation.y = 1
			current_scene.add_child(characterCollision)
			characterCollision.set_owner(current_scene)
	
		# Blend Tree
		blendTree = AnimationNodeBlendTree.new()
		stateMachine = AnimationNodeStateMachine.new()
		blendTree.add_node(animationNodeName, stateMachine, Vector2.ZERO)
		blendTree.connect_node(outputNode, 0, animationNodeName)
		
		# AnimationTree Position
		blendTree.set_node_position(animationNodeName, animationNodePosition)
		blendTree.set_node_position(outputNode, outputNodePosition)

		# Animation Tree
		animationTree = AnimationTree.new()
		animationTree.anim_player = animationPlayerPath
		animationTree.process_mode = AnimationTree.ANIMATION_PROCESS_PHYSICS
#		animationTree.root_motion_track = rootMotionTrackPath
		animationTree.tree_root = blendTree
		animationTree.active = true
		current_scene.add_child(animationTree)
		animationTree.set_owner(current_scene)

		# RootMotion View
		if armature_rootmotion_view:
			rootMotionView = RootMotionView.new()
	#		rootMotionView.animation_path = animationPlayerPath
			current_scene.add_child(rootMotionView)
			rootMotionView.set_owner(current_scene)


func _addStateNode(stateMachine, animation, statePosition):
	var newAnimation = AnimationNodeAnimation.new()
	newAnimation.animation = animation
	stateMachine.add_node(animation, newAnimation)
	stateMachine.set_node_position(animation, statePosition)


func _addStateMachine(currentScene, stateMachineData):
	# State Machine Params
	var stateMachineNodeName = stateMachineData.nodeName
	var states = stateMachineData.states
	var stateTransitions = stateMachineData.stateTransitions

	# Get Animation Tree
	var animationTreeNode = currentScene.find_node(animation_tree_node_name, true).tree_root
	if animationTreeNode.has_node(stateMachineNodeName):

		# Procedural StateMachine Generation
		var stateMachine = animationTreeNode.get_node(stateMachineNodeName)
		var initialAnimation
		# Generate States
		for state in states: 
			var stateName = state["name"]
			if not initialAnimation: initialAnimation = stateName
			var statePosition = Vector2(state["positionX"], state["positionY"])
			_addStateNode(stateMachine, stateName, statePosition)

		# Connect States Transitions
		for transition in stateTransitions:
			var fromT = transition["from"]
			var toT = transition["to"]
			var xFadeTimeT = transition["xFadeTime"]
			var switchModeIndex = transition["switchMode"]
			_addStateTransition(stateMachine, fromT, toT, xFadeTimeT, switchModeIndex)

		# Add Animation States
		for state in states:
			# Remove Loop Names
			var stateName = state["name"]
			var animationNameLoopLess = stateName.replace("-loop", "")
			stateMachine.rename_node(stateName, animationNameLoopLess)

		# Setup Initial Animation
		if initialAnimation: 
			initialAnimation = initialAnimation.replace("-loop", "")
			stateMachine.set_start_node(initialAnimation)


func _addStateTransition(stateMachine, from, to, xFadeTime, switchModeIndex):
	var newTransition = AnimationNodeStateMachineTransition.new()
	newTransition.xfade_time = xFadeTime
	var switchMode
	if switchModeIndex == 0: switchMode = AnimationNodeStateMachineTransition.SWITCH_MODE_IMMEDIATE
	if switchModeIndex == 1: switchMode = AnimationNodeStateMachineTransition.SWITCH_MODE_SYNC
	if switchModeIndex == 2: switchMode = AnimationNodeStateMachineTransition.SWITCH_MODE_AT_END
	newTransition.switch_mode = switchMode
	stateMachine.add_transition(from, to, newTransition)
