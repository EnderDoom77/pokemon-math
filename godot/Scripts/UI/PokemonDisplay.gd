class_name PokemonDisplay
extends Node

@export var pokemon_id: String = ""
@export var type_container: TypeContainer
@export var image_display: TextureRect
@export var name_display: Label
@export var elo_display: EloInfoDisplay
@export var extra_displays: Dictionary

var pokemon: PokemonLib.Pokemon = null
var elo: float = -1
var extra_data: Dictionary

var config: PokemonLib.Config = PokemonLib.get_config()
var pokedex: Dictionary = PokemonLib.get_pokedex()

const POKEMON_SWITCH_DURATION = 0.5

# Called when the node enters the scene tree for the first time.
func _ready():
	if pokemon_id and pokemon_id in pokedex:
		set_pokemon(pokedex[pokemon_id])

func set_pokemon_data_no_wait():
	self.type_container.set_types(pokemon.types)
	self.image_display.texture = pokemon.get_image()
	self.name_display.text = pokemon.name
	var current_save = SessionManager.get_singleton().current_save
	self.elo_display.set_values(current_save.get_info(pokemon.id))

@warning_ignore("shadowed_variable")
func set_pokemon(pokemon: PokemonLib.Pokemon):
	self.pokemon_id = pokemon.id
	self.pokemon = pokemon
	var displays: Array[CanvasItem] = [type_container, name_display, image_display, elo_display]
	var tween = create_tween()
	if not tween:
		set_pokemon_data_no_wait()
		push_error("Unable to create tween for set pokemon!")
		return
		
	tween.set_parallel(true)
	tween.chain()
	for display in displays:
		tween.tween_property(display, "modulate:a", 0, POKEMON_SWITCH_DURATION / 2)
	
	tween.tween_callback(set_pokemon_data_no_wait)
	
	tween.chain()
	for display in displays:
		tween.tween_property(display, "modulate:a", 1, POKEMON_SWITCH_DURATION / 2)

## A function that allows for the modification of one of the configured extra displays, 
## the function must take the display node as its only parameter
func set_data(data_name: String, data: String, function: Callable = func(_node: Node): pass):
	if data_name not in extra_displays:
		push_error("Unable to find data name %s in pokemon display!" % data_name)
		return
	extra_data[data_name] = data
	function.call(get_node(extra_displays[data_name]))
	
## A simplified form of set data where the target display is a Label
func set_data_simple(data_name, data: String):
	if data_name not in extra_displays:
		push_error("Unable to find data name %s in pokemon display!" % data_name)
		return
	var display: Label = get_node(extra_displays[data_name])
	if not display:
		push_error("Attempted to use simple data setter on an extra display which is not a label")
		return
	extra_data[data_name] = data
	display.text = data
	
@warning_ignore("shadowed_variable")
func set_elo(elo: float):
	self.elo = elo
	var config = PokemonLib.get_config()
	
