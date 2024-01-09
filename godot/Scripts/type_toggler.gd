class_name TypeToggler

extends HBoxContainer

@export var btn: Button
@export var include_type_icon: bool = true
@export var include_type_name: bool = false
@export var type_name_tint: float = 0.2

@export var overlay_image: TextureRect

@export var overlay_forbidden: Texture2D
@export var overlay_allowed: Texture2D
@export var overlay_required: Texture2D

var toggle_state: PokemonLib.ToggleState = PokemonLib.ToggleState.ALLOW
var toggle_overlays: Dictionary

var poke_type: PokemonLib.PokeType

signal toggled

# Called when the node enters the scene tree for the first time.
func _ready():
	btn.pressed.connect(_on_pressed)
	toggle_overlays[PokemonLib.ToggleState.FORBID] = overlay_forbidden
	toggle_overlays[PokemonLib.ToggleState.ALLOW] = overlay_allowed
	toggle_overlays[PokemonLib.ToggleState.REQUIRE] = overlay_required
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass
	
func set_type(type: PokemonLib.PokeType):
	self.poke_type = type
	var config = PokemonLib.get_config()
	if include_type_icon:
		var icon = config.type_images[type]
		btn.icon = icon
	else:
		btn.icon = null
	
	if include_type_name:
		btn.text = PokemonLib.poke_type_names[type]
		var font_color = MathLib.max_contrast(config.type_colors[type], type_name_tint)
		for style in ["_", "_pressed", "_hover", "_focus", "_hover_pressed"]:
			btn.add_theme_color_override("font%s_color" % style, font_color)
	else:
		btn.text = ""

func reset_state(notify: bool = true):
	set_state(PokemonLib.ToggleState.ALLOW, notify)

func set_state(new_state: PokemonLib.ToggleState, notify: bool = true):
	toggle_state = new_state
	overlay_image.texture = toggle_overlays[toggle_state]
	if notify: toggled.emit(toggle_state)

func _on_pressed():
	set_state((toggle_state + 1) % len(PokemonLib.ToggleState))
