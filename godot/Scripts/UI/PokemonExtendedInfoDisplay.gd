class_name PokemonExtendedInfoDisplay
extends PokemonDisplay

@export var effectiveness_container: Node
@export var effectiveness_prefab: PackedScene

@export var ability_display: GenericInfoDisplay
@export var stats_display: GenericInfoDisplay
@export var height_display: GenericInfoDisplay
@export var weight_display: GenericInfoDisplay
@export var gender_ratio_display: GenericInfoDisplay
@export var prevo_display: GenericInfoDisplay
@export var evos_display: GenericInfoDisplay

# Called when the node enters the scene tree for the first time.
func _ready():
	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass

static func format_abilities(pokemon: PokemonLib.Pokemon, config: PokemonLib.Config) -> String:
	var descriptions: Array[String] = []
	for ability in pokemon.abilities:
		var hidden = pokemon.hidden_abilities.contains(ability)
		descriptions.append(PokemonExtendedInfoDisplay.format_ability(ability, config, hidden))
	return "\n".join(descriptions)

static func format_ability(ability_name: String, config: PokemonLib.Config, hidden: bool = false) -> String:
	var desc = config.get_ability_description(ability_name)
	return ("[i][b]%s (H)[/b]: %s[/i]" if hidden else "[b]%s[/b]: %s") % [ability_name, desc]

static func format_gender(gender: String, config: PokemonLib.Config, extra_text:String = ""):
	var color: Color = config.gender_colors.get(gender, Color.BLACK)
	var hex_code: String = color.to_html(false)
	return "[color=#%s]%s%s[/color]" % [hex_code, gender, extra_text]

static func format_gender_ratio(gender_ratio: Dictionary, config: PokemonLib.Config):
	var items = []
	for gender in gender_ratio:
		items.append(PokemonExtendedInfoDisplay.format_gender(gender, config, ": %.1f%%" % (gender_ratio[gender] * 100)))
	return " | ".join(items)

static func format_stats(stats: Array[int], _config: PokemonLib.Config) -> String:
	var items = []
	for stat in PokemonLib.PokeStat.values():
		items.append("%s: %d" % [PokemonLib.poke_stat_abbrev[stat], stats[stat]])
	return "\n".join(items)

@warning_ignore("shadowed_variable")
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
		
	if ability_display != null:
		ability_display.set_data("Abilities: %s" % ", ".join(pokemon.abilities), PokemonExtendedInfoDisplay.format_abilities(pokemon, config))
	if stats_display != null:
		stats_display.set_data("Stats", format_stats(pokemon.base_stats, config))
	if weight_display != null:
		weight_display.set_data("Weight", "%.1f kg" % pokemon.weightkg)
	if height_display != null:
		height_display.set_data("Height", "%.1f m" % pokemon.heightm)
	if gender_ratio_display != null:
		var has_set_gender = pokemon.gender != ""
		var has_gender_ratio = pokemon.gender_ratio != {}
		gender_ratio_display.set_visible(has_set_gender or has_gender_ratio)
		if has_set_gender:
			gender_ratio_display.set_data("Gender", PokemonExtendedInfoDisplay.format_gender(pokemon.gender, config))
		elif has_gender_ratio:
			gender_ratio_display.set_data("Gender Ratio", PokemonExtendedInfoDisplay.format_gender_ratio(pokemon.gender_ratio, config))
	
	if prevo_display != null:
		prevo_display.set_visible(pokemon.preevolution != "")
		if pokemon.preevolution:
			prevo_display.set_data("Pre-evolution", pokemon.preevolution)
	
	if evos_display != null:
		evos_display.set_visible(pokemon.evolutions != [])
		if pokemon.evolutions:
			evos_display.set_data("Evolution", " | ".join(pokemon.evolutions)) 
		
	
