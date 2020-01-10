extends Spatial

#################
# JOYPAD
# You may need to adjust depending on the sensitivity of your joypad
var JOYPAD_SENSITIVITY_Y = 4
var JOYPAD_SENSITIVITY_X = 2

const JOYPAD_DEADZONE = 0.15
const CAMERA_ROTATION_SPEED = .005 #0.001
const CAMERA_X_ROT_MIN = -30
const CAMERA_X_ROT_MAX = 40
var camera_x_rot = 0.0

var lock_camera = false

var _CameraManager

func _input(event):
	if event is InputEventMouseMotion:
		_CameraManager.rotate_y( - event.relative.x * CAMERA_ROTATION_SPEED )
		_CameraManager.orthonormalize() # after relative transforms, camera needs to be renormalized
		camera_x_rot = clamp(camera_x_rot + event.relative.y * CAMERA_ROTATION_SPEED,deg2rad(CAMERA_X_ROT_MIN), deg2rad(CAMERA_X_ROT_MAX) )
		_CameraManager.get_node('CameraRotation').rotation.x = camera_x_rot

# For Gamepads | Xbox/Steam/ETC
func process_joypad_input(delta):
	# ----------------------------------
	# Joypad rotation
	var joypad_vec = Vector2()
	if Input.get_connected_joypads().size() > 0:

		if OS.get_name() == "Windows":
			joypad_vec = Vector2(Input.get_joy_axis(0, 2), Input.get_joy_axis(0, 3))
		elif OS.get_name() == "X11":
			joypad_vec = Vector2(Input.get_joy_axis(0, 3), Input.get_joy_axis(0, 4))
		elif OS.get_name() == "OSX":
			joypad_vec = Vector2(Input.get_joy_axis(0, 3), Input.get_joy_axis(0, 4))

		# If the vector length of the joypad from a to b is less than the joypad deadzone, do nothing.
		# This prevents jittering.
		if joypad_vec.length() < JOYPAD_DEADZONE:
			joypad_vec = Vector2(0, 0)
		else:
			joypad_vec = joypad_vec.normalized() * ((joypad_vec.length() - JOYPAD_DEADZONE) / (1 - JOYPAD_DEADZONE))

		##############################################
		# Rotate Our Camera
		
		if not lock_camera:
			# Rotate Camera Y
			_CameraManager.rotate_y( deg2rad(joypad_vec.x * JOYPAD_SENSITIVITY_Y * -1))
			_CameraManager.orthonormalize() # after relative transforms, camera needs to be renormalized

			# Rotate Camera X Rotation clamp(value, minimum, maximum)
			# Since we are NOT using _input(event) and instead relying on delta, we need to rotate_x, but CLAMP
			# If we pass a threshold.

			_CameraManager.get_node('CameraRotation').rotate_x(deg2rad(joypad_vec.y * JOYPAD_SENSITIVITY_X))
			_CameraManager.get_node('CameraRotation').rotation.x = clamp(_CameraManager.get_node('CameraRotation').rotation.x, deg2rad(CAMERA_X_ROT_MIN), deg2rad(CAMERA_X_ROT_MAX) )