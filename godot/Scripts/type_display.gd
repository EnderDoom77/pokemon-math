class_name TypeDisplay

extends PanelContainer

@export var text_tint: float = 0.2
@export var label: Label

var poke_type: PokemonLib.PokeType
var color: Color
var text_color: Color

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

@warning_ignore("shadowed_variable")
func stylebox_from_color(color: Color) -> StyleBox:
	var result: StyleBoxFlat = self.get_theme_stylebox("panel")
	result.bg_color = color
	return result

func set_type(type: PokemonLib.PokeType):
	if type == PokemonLib.PokeType.NONE:
		self.visible = false
		return
	self.visible = true
	label.text = PokemonLib.poke_type_names[type]
	var config = PokemonLib.get_config()
	self.poke_type = type
	self.color = config.type_colors[type]
	self.text_color = MathLib.max_contrast(self.color, text_tint)
	# self.add_theme_stylebox_override("panel", stylebox_from_color(self.color))
	self.self_modulate = self.color

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
