extends Spatial

func _physics_process(delta):
	
	if Input.is_action_just_pressed("SayLoser"):
		$AnimationTree['parameters/OneShot/active'] = true
	
	elif Input.is_action_pressed("MoveUp") and Input.is_action_pressed("IncreaseLocomotion"):
		$AnimationTree['parameters/Locomo/blend_position'] = 2
		
	elif Input.is_action_pressed("MoveUp"):
		$AnimationTree['parameters/Locomo/blend_position'] = 1
		
	else:
		$AnimationTree['parameters/Locomo/blend_position'] = 0