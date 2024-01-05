class_name PokemonExtendedInfoDisplay
extends PokemonDisplay

@export var effectiveness_container: Node
@export var effectiveness_prefab: PackedScene

# Called when the node enters the scene tree for the first time.
func _ready():
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func set_pokemon_extended(pokemon: PokemonLib.Pokemon):
	self.set_pokemon(pokemon)
	var config := PokemonLib.get_config()
	var effectiveness: Array[float] = PokemonLib.get_effectiveness(pokemon.types, config)
	var types_by_effectiveness: Dictionary = CollectionUtils.invert_dictionary(CollectionUtils.array_to_dictionary(effectiveness))
	for child in effectiveness_container.get_children():
		effectiveness_container.remove_child(child)
	var effectiveness_levels = types_by_effectiveness.keys()
	effectiveness_levels.sort()
	for key in effectiveness_levels:
		var types: Array[PokemonLib.PokeType] = []
		types.assign(types_by_effectiveness[key])
		var info: EffectivenessInfo = effectiveness_prefab.instantiate()
		effectiveness_container.add_child(info)
		info.set_effectiveness(key)
		info.set_types(types, config)
