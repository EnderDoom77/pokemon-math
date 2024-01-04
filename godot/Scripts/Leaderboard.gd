class_name Leaderboard
extends Control

@export var leaderboard_item: PackedScene
@export var leaderboard_container: Node
@export var auto_refresh: bool = true

enum SortType {NAME, NUMBER, ELO, ELO_DELTA}

var pokemon_displays: Array[PokemonDisplay]
var pokedex: Dictionary

var sort_type: SortType = SortType.NAME
var sort_ascending: bool = true
var filter_types: Dictionary
var filter_name: String = ""
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
	var save_data: SaveManager.SaveData = SessionManager.get_singleton().current_save
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
	if filter_eligible != PokemonLib.ToggleState.ALLOW:
		var contained = save_eligible.contains(pokemon.id)
		var allowed = filter_eligible == PokemonLib.ToggleState.REQUIRE
		if allowed != contained: return false
	if filter_name and not PokemonLib.normalize_name(pokemon.id).contains(filter_name):
		return false
	for type in config.types:
		if filter_types[type] == PokemonLib.ToggleState.ALLOW: continue
		var contained = type in pokemon.types
		var allowed = filter_types[type] == PokemonLib.ToggleState.REQUIRE
		if allowed != contained: return false
	return true

## Sorts a given list in-place by the current leaderboard sort settings.
func sort_pokemon(list: Array[PokemonLib.Pokemon]):
	var comparer: Callable
	match sort_type:
		SortType.NAME:
			comparer = func(a: PokemonLib.Pokemon, b: PokemonLib.Pokemon) -> bool:
				return (a.name.to_lower() < b.name.to_lower()) == sort_ascending # same as XNOR
		SortType.NUMBER:
			comparer = func(a: PokemonLib.Pokemon, b: PokemonLib.Pokemon) -> bool:
				return (a.num < b.num) == sort_ascending
		SortType.ELO:
			var elo_lookup: Dictionary = build_elo_lookup_dictionary(list.map(func(p): return p.id))
			comparer = func(a: PokemonLib.Pokemon, b: PokemonLib.Pokemon) -> bool:
				return (elo_lookup[a.id].elo < elo_lookup[b.id].elo) == sort_ascending
		SortType.ELO_DELTA:
			var elo_lookup: Dictionary = build_elo_lookup_dictionary(list.map(func(p): return p.id))
			comparer = func(a: PokemonLib.Pokemon, b: PokemonLib.Pokemon) -> bool:
				return (abs(elo_lookup[a.id].elo_delta()) < abs(elo_lookup[b.id].elo_delta())) == sort_ascending
		_:
			push_error("Attempting to sort with some invalid sort type value: %d" % sort_type)
			return
	list.sort_custom(comparer)

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

func on_save_changed():
	update_item_display()
