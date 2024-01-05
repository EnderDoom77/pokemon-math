class_name PokeInfoPopup
extends PopupPanel

static var instance: PokeInfoPopup
@export var pokemon_display: PokemonExtendedInfoDisplay

# Called when the node enters the scene tree for the first time.
func _ready():
	self.instance = self

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func set_and_show(pokemon: PokemonLib.Pokemon):
	self.popup()
	pokemon_display.set_pokemon_extended(pokemon)
