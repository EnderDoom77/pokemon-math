class_name TypeContainer

extends HBoxContainer

@export var type_display_1: TypeDisplay = null
@export var type_display_2: TypeDisplay = null

var type1: PokemonLib.PokeType = PokemonLib.PokeType.NONE
var type2: PokemonLib.PokeType = PokemonLib.PokeType.NONE

func set_types(types: Array[PokemonLib.PokeType]):
	type1 = PokemonLib.PokeType.NONE
	type2 = PokemonLib.PokeType.NONE
	if len(types) >= 1:
		type1 = types[0]
		if len(types) >= 2:
			type2 = types[1]
	
	type_display_1.set_type(type1)
	type_display_2.set_type(type2)
