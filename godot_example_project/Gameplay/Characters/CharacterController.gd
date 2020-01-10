#########################
# CharacterController.gd 
# Should be appropriately named CharacterPlayerMovement, this
# script handles applies the player's input to the Character's 
# movement.

extends KinematicBody

class_name CharacterController

const GRAVITY = Vector3(0,-9.8, 0)
const MOTION_INTERPOLATE_SPEED = 10
const ROTATION_INTERPOLATE_SPEED = 10

# Exported Variables
export(Resource) var anim_attack_one
export(Resource) var anim_attack_two

export(float) var default_locomotion_speed = 1.0
export(float) var character_height = 1.0
export(Vector3) var camera_offset = Vector3(0.0, 1.25, 0.0)

var is_sprinting : bool = false
var root_motion : Transform = Transform()
var velocity : Vector3 = Vector3()


var orientation : Transform = Transform()
var motion : Vector2 = Vector2()


func _ready():
	_CameraManager.global_transform.origin.y = character_height
	
	orientation = self.global_transform
	orientation.origin = Vector3.ZERO

func _input(event):
	if event.is_action_pressed("quit"):
		get_tree().quit()
			
func _physics_process(delta):
	process_movement(delta)

# Process movement utilizing the Kinematic Character's Root Motion
# 1.) Gather Input from player
# 2.) Set the appropriate animation tree properties
# 3.) If a user performs an action like a dodge or a jump, then
#     perform that action and calculate it into the root motion as well.

const IDLE_MONTAGE_DELAY_INTERVAL = 5
var idle_montage_delay_timer : float = 0.0

func process_movement(delta):
	
	# Bring the camera along for the ride
	_CameraManager.global_transform.origin = Vector3(\
		self.global_transform.origin.x + self.camera_offset.x, \
		self.global_transform.origin.y + self.camera_offset.y, \
		self.global_transform.origin.z + self.camera_offset.z)
		
	var motion_target = Vector2( 	Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
									Input.get_action_strength("move_forward") - Input.get_action_strength("move_backward") )

	motion = motion.linear_interpolate(motion_target, MOTION_INTERPOLATE_SPEED * delta)

	var q_from = Quat(orientation.basis)
	var q_to = Quat()
	
	# Get the Camera's Rotation
	# Z IS REVERSED IN GODOT according to OpenGL Standards
	var cam_z = - _CameraManager.activeCamera.global_transform.basis.z
	var cam_x = _CameraManager.activeCamera.global_transform.basis.x

	cam_z.y=0
	cam_z = cam_z.normalized()
	cam_x.y=0
	cam_x = cam_x.normalized()

	var motion_length = motion.length()

	is_sprinting = Input.is_action_pressed("sprint")

	if is_sprinting:
		motion_length *= 2
		
	$AnimationTree["parameters/default_locomotion/blend_position"] = motion_length
	
	#idle_montage_delay_timer += delta
	#if idle_montage_delay_timer > IDLE_MONTAGE_DELAY_INTERVAL:
	#	var idle_do = rand_range(0.0, 1.0)
	#	if idle_do > 0.5:
	#		$AnimationTree["parameters/IdleMontage/active"] = true
	#	else:
	#		$AnimationTree["parameters/IdleMontage/active"] = false
	#		
	#	idle_montage_delay_timer = 0.0
	
	# SMOOTHLY ROTATE FROM ONE QUATERNION TO ANOTHER:
	# ROTATES CHARACTER TO THE CAMERA.
	var target = - cam_x * motion.x -  cam_z * motion.y
	if (target.length() > 0.001):
		q_to = Quat(Transform().looking_at(target,Vector3(0,1,0)).basis)

	# interpolate current rotation with desired one
	orientation.basis = Basis(q_from.slerp(q_to,delta*ROTATION_INTERPOLATE_SPEED))
		
	#######################
	# Character movement processing.

	# get root motion transform
	root_motion = $AnimationTree.get_root_motion_transform()

	# apply root motion to orientation
	orientation *= root_motion

	var h_velocity = orientation.origin / delta
	velocity.x = h_velocity.x
	velocity.z = h_velocity.z
	velocity += GRAVITY * delta
	velocity = move_and_slide(velocity,Vector3(0,1,0))

	orientation.origin = Vector3() #clear accumulated root motion displacement (was applied to speed)
	# orthonormalize orientation, make sure it's orthogonal to normal.
	orientation = orientation.orthonormalized()

	# Basis stores the rotation and scale of a spatial. See Godot Docs regarding the BASIS class and how it is used.
	global_transform.basis = orientation.basis