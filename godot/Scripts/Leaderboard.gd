class_name Leaderboard
extends Control

@export var leaderboard_item: PackedScene
@export var leaderboard_container: Node
@export var auto_refresh: bool = true

enum SortType {NAME, NUMBER, ELO, ELO_DELTA}

var pokemon_displays: Array[PokemonDisplay]
var pokedex: Dictionary

var sort_type: SortType = SortType.ELO
var sort_ascending: bool = false
var filter_types: Dictionary
var filter_name: String = ""
var filter_pure: PokemonLib.ToggleState = PokemonLib.ToggleState.ALLOW
var filter_eligible: PokemonLib.ToggleState = PokemonLib.ToggleState.REQUIRE

func _ready():
	var config := PokemonLib.get_config()
	for t in config.types:
		filter_types[t] = PokemonLib.ToggleState.ALLOW
	pokedex = PokemonLib.get_pokedex()
	SessionManager.get_singleton().on_save_changed.connect(on_save_changed)
	update_item_display()

func _process(_delta):
	pass

func get_display(index: int) -> PokemonDisplay:
	while index >= len(pokemon_displays):
		var pokemon_display_node: Node = leaderboard_item.instantiate()
		var pokemon_display: PokemonDisplay = pokemon_display_node
		leaderboard_container.add_child(pokemon_display_node)
		pokemon_displays.append(pokemon_display)
		pokemon_display.set_data_simple("rank", "#%d" % (index + 1))
	return pokemon_displays[index]

func update_item_display():
	var all_pokemon: Array[PokemonLib.Pokemon] = []
	all_pokemon.assign(pokedex.values())
	var filtered: Array[PokemonLib.Pokemon] = get_filtered(all_pokemon)
	sort_pokemon(filtered)
	for i in range(len(filtered)):
		var display = get_display(i)
		display.set_pokemon(filtered[i])
		display.visible = true
	for i in range(len(filtered), len(pokemon_displays)):
		pokemon_displays[i].visible = false

func get_filtered(pokemon_list: Array[PokemonLib.Pokemon]) -> Array[PokemonLib.Pokemon]:
	var save_eligible := MathLib.Set.new(SessionManager.get_singleton().current_save.eligible_pokemon)
	return pokemon_list.filter(func(p): return filter_pokemon(p, save_eligible))
	
func filter_pokemon(pokemon: PokemonLib.Pokemon, save_eligible: MathLib.Set) -> bool:
	var config: PokemonLib.Config = PokemonLib.get_config()
	if not PokemonLib.is_allowed_by_filter(filter_eligible, save_eligible.contains(pokemon.id)):
		return false
	if filter_name and not PokemonLib.normalize_name(pokemon.id).contains(filter_name):
		return false
	if not PokemonLib.is_allowed_by_filter(filter_pure, len(pokemon.types) == 1):
		return false
	for type in config.types:
		if not PokemonLib.is_allowed_by_filter(filter_types[type], type in pokemon.types):
			return false
	return true

## Constructs a comparer between multiple pokemon from a function that gets a single key attribute given a pokemon
func pokemon_comparer(key: Callable, invert: bool = false) -> Callable:
	return func(p1: PokemonLib.Pokemon, p2: PokemonLib.Pokemon):
		var k1 = key.call(p1)
		var k2 = key.call(p2)
		if k1 == k2:
			return default_pokemon_comparer(p1,p2,invert)
		else:
			return (k1 < k2) != invert
		
func default_pokemon_comparer(p1: PokemonLib.Pokemon, p2: PokemonLib.Pokemon, invert: bool = false):
	return (p1.id < p2.id) != invert

## Sorts a given list in-place by the current leaderboard sort settings.
func sort_pokemon(list: Array[PokemonLib.Pokemon]):
	var key: Callable
	match sort_type:
		SortType.NAME:
			key = func(p: PokemonLib.Pokemon): return p.name
		SortType.NUMBER:
			key = func(p: PokemonLib.Pokemon): return p.num
		SortType.ELO:
			var elo_lookup: Dictionary = build_elo_lookup_dictionary(list.map(func(p): return p.id))
			var default_elo = SaveManager.PokeEloData.new()
			key = func(p: PokemonLib.Pokemon):
				return elo_lookup.get(p.id, default_elo).elo
		SortType.ELO_DELTA:
			var elo_lookup: Dictionary = build_elo_lookup_dictionary(list.map(func(p): return p.id))
			var default_elo = SaveManager.PokeEloData.new()
			key = func(p: PokemonLib.Pokemon):
				return abs(elo_lookup.get(p.id, default_elo).elo_delta())
		_:
			push_error("Attempting to sort with some invalid sort type value: %d" % sort_type)
			return
	list.sort_custom(pokemon_comparer(key,!sort_ascending))

## Returns a dictionary linking the pokemon IDs from `keys` to elo information objects.
func build_elo_lookup_dictionary(keys: Array) -> Dictionary:
	var result := {}
	var save = SessionManager.get_singleton().current_save
	for pokemon_id in keys:
		result[pokemon_id] = save.elo_info[pokemon_id]
	return result

func _on_name_filter_changed(content: String):
	filter_name = content
	if auto_refresh: update_item_display()

func _on_type_filter_changed(types: Dictionary):
	filter_types = types
	if auto_refresh: update_item_display()

func _on_refresh_requested():
	update_item_display()
	
func _on_auto_refresh_toggled(new_state: bool):
	if new_state:
		update_item_display()
	auto_refresh = new_state

func _on_sort_type_changed(sort: String):
	match sort:
		"name":
			sort_type = SortType.NAME
		"number":
			sort_type = SortType.NUMBER
		"elo":
			sort_type = SortType.ELO
		"elo_delta":
			sort_type = SortType.ELO_DELTA
		_:
			push_error("Received invalid sort type: %s" % sort)
			return
	if auto_refresh: update_item_display()

func _on_sort_mode_changed(mode: String):
	match mode:
		"ascending":
			sort_ascending = true
		"descending":
			sort_ascending = false
		_:
			push_error("Received invalid sort mode: %s" % mode)
			return
	
	if auto_refresh: update_item_display()


const _INTERNAL_SORT_TYPE_ITEMS = ["name", "number", "elo", "elo_delta"]
func _on_sort_type_item_selected(index: int):
	_on_sort_type_changed(_INTERNAL_SORT_TYPE_ITEMS[index])

const _INTERNAL_SORT_MODE_ITEMS = ["ascending", "descending"]
func _on_sort_mode_item_selected(index: int):
	_on_sort_mode_changed(_INTERNAL_SORT_MODE_ITEMS[index])

func _on_filter_purity_toggled(toggle_state: PokemonLib.ToggleState):
	filter_pure = toggle_state
	if auto_refresh: update_item_display()

func on_save_changed():
	update_item_display()
