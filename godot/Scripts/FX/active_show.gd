extends Button

@export var active: bool = true
@export var target_node: Node = self
@export var animated_properties: Array[String] = [] 
@export var target_values: Array[Variant] = []
@export var interval: float = 1.0
var original_values: Array[Variant] = []

var tween: Tween = null

# Called when the node enters the scene tree for the first time.
func _ready():
	tween = create_tween().set_loops().set_parallel(true)
	assert(len(animated_properties) == len(target_values))
	for prop in animated_properties:
		original_values.append(target_node.get(prop))
	
	tween.chain()
	for i in range(len(animated_properties)):
		tween.tween_property(target_node, animated_properties[i], target_values[i], interval / 2)
	tween.chain()
	for i in range(len(animated_properties)):
		tween.tween_property(target_node, animated_properties[i], original_values[i], interval / 2)
	tween.stop()
	
	if active:
		activate()

func _process(_delta):
	pass

@warning_ignore("shadowed_variable")
func set_active(active: bool):
	if self.active == active: return
	self.active = active
	if active:
		activate()
	else:
		deactivate()

func activate():
	if not tween:
		push_error("Attempted to activate an active animator before the node entered the scene tree, or its tweener was killed.")
		return
	tween.play()

func deactivate():
	tween.stop()
	for i in range(len(animated_properties)):
		self.set(animated_properties[i], original_values[i])
