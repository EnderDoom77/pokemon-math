class_name TypeSelector

extends Button

signal selection_changed(types: Dictionary)
@export var popup: PopupPanel
@export var type_container: Node
@export var type_toggler_prefab: PackedScene

var type_toggles: Dictionary
var current_selection: Dictionary

# Called when the node enters the scene tree for the first time.
func _ready():
	var config = PokemonLib.get_config()
	popup.close_requested.connect(func(): _on_toggled(false))
	
	for t in config.types:
		var type_toggler: TypeToggler = type_toggler_prefab.instantiate()
		type_toggler.set_type(t)
		current_selection[t] = type_toggler.toggle_state
		type_toggles[t] = type_toggler
		type_container.add_child(type_toggler)
		type_toggler.toggled.connect(func(new_state): _on_type_toggled(t, new_state))

func reset_selections():
	for type_toggle: TypeToggler in type_toggles.values():
		type_toggle.reset_state(false)
		current_selection[type_toggle.poke_type] = type_toggle.toggle_state
	selection_changed.emit(current_selection)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass
	
func _on_toggled(toggled_on):
	if toggled_on:
		popup.popup()
	else:
		popup.hide()

func _on_type_toggled(type: PokemonLib.PokeType, new_state: PokemonLib.ToggleState):
	current_selection[type] = new_state
	selection_changed.emit(current_selection)

func _on_reset_button_pressed():
	reset_selections()
