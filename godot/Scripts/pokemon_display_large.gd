extends Node

@export var pokemon_id: String = ""
@export var type_container: TypeContainer
@export var image_display: TextureRect
@export var name_display: Label
@export var extra_displays: Dictionary

var pokemon: PokemonLib.Pokemon = null
var extra_data: Dictionary

var config: PokemonLib.Config = PokemonLib.get_config()
var pokedex: Dictionary = PokemonLib.get_pokedex()

# Called when the node enters the scene tree for the first time.
func _ready():
	if pokemon_id and pokemon_id in pokedex:
		set_pokemon(pokedex[pokemon_id])

@warning_ignore("shadowed_variable")
func set_pokemon(pokemon: PokemonLib.Pokemon):
	self.pokemon_id = pokemon.id
	self.type_container.set_types(pokemon.types)
	self.image_display.texture = pokemon.get_image()
	self.name_display.text = pokemon.name

func set_data(data_name: String, data: String, function: Callable = func(_node: Node): pass):
	if data_name not in extra_displays:
		push_error("Unable to find data name %s in pokemon display!" % data_name)
		return
	extra_data[data_name] = data
	function.call(extra_displays[data_name])
