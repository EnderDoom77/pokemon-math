extends Button

@export var image_expanded: Texture2D
@export var image_collapsed: Texture2D
@export var target: Node

# Called when the node enters the scene tree for the first time.
func _ready():
	self.toggled.connect(on_button_toggled)

func on_button_toggled(collapsed: bool):
	target.visible = not collapsed
	self.icon = image_collapsed if collapsed else image_expanded
