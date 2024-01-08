class_name EffectivenessInfo
extends PanelContainer

@export var effectiveness_label: Label
@export var type_container: Node
@export var label_gradient: Gradient
@export var label_gradient_range: float = 4.00

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass

func get_nth_type_indicator(index: int) -> TextureRect:
	var children = type_container.get_children()
	while index >= len(children):
		var new_child := TextureRect.new()
		children.append(new_child)
		type_container.add_child(new_child)
		new_child.expand_mode = TextureRect.EXPAND_FIT_HEIGHT_PROPORTIONAL
		new_child.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	
	return children[index]

func set_effectiveness(value: float):
	effectiveness_label.text = "%d%%" % roundi(value * 100)
	effectiveness_label.add_theme_color_override("font_color", label_gradient.sample(value / label_gradient_range))

func set_types(types: Array[PokemonLib.PokeType], config: PokemonLib.Config):
	for i in range(len(types)):
		var type = types[i]
		var indicator = get_nth_type_indicator(i)
		indicator.texture = config.type_images[type]
		indicator.visible = true
	for i in range(len(types), type_container.get_child_count()):
		type_container.get_child(i).visible = false
	
