class_name FilterToggler
extends Button

@export var overlay_image: TextureRect

@export var overlay_forbidden: Texture2D
@export var overlay_allowed: Texture2D
@export var overlay_required: Texture2D

@export var toggle_state: PokemonLib.ToggleState = PokemonLib.ToggleState.ALLOW
var default_state: PokemonLib.ToggleState
var toggle_overlays: Dictionary

signal toggled_filter(toggle_state: PokemonLib.ToggleState)

# Called when the node enters the scene tree for the first time.
func _ready():
	default_state = toggle_state
	self.pressed.connect(_on_pressed)
	toggle_overlays[PokemonLib.ToggleState.FORBID] = overlay_forbidden
	toggle_overlays[PokemonLib.ToggleState.ALLOW] = overlay_allowed
	toggle_overlays[PokemonLib.ToggleState.REQUIRE] = overlay_required
	overlay_image.texture = toggle_overlays[default_state]
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass

func reset_state(notify: bool = true):
	set_state(default_state, notify)

func set_state(new_state: PokemonLib.ToggleState, notify: bool = true):
	toggle_state = new_state
	overlay_image.texture = toggle_overlays[toggle_state]
	if notify: toggled_filter.emit(toggle_state)

func _on_pressed():
	set_state((toggle_state + 1) % len(PokemonLib.ToggleState))
