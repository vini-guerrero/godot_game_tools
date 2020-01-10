extends Spatial

class_name CameraManager

var activeCamera : Camera
var thirdPersonCamera : Camera
var pointAndClick : Camera 
var is_assigned_to_player : bool = false

var in_battle_mode : Node

# Bodies of interest should hold opponents, friends, items, areas, etc.
var bodies_of_interest = { 'opponents' : {}, 'friends' : {}, 'npcs' : {}, 'items' : {}, 'areas' : {}, 'etc' : {} }

var lock_camera_rotation = false

func _ready():
	print('READY CameraManager')
	
	thirdPersonCamera = find_node('Camera_ThirdPerson', true, false)
	pointAndClick = find_node('Camera_PointAndClick', true, false)
	
	activeCamera = thirdPersonCamera
	activeCamera._CameraManager = self
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
		
	activeCamera.current = true

const CAMERA_HEIGHT = 1.25
const CAMERA_TRAVEL_SPEED = 3
var camera_travel_timer = 0.0
var start_camera_travel = false
var camera_old_position
		
func _physics_process(delta):
	pass