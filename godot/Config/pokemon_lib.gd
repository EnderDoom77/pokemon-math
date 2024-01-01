class_name PokemonLib
extends Object

enum PokeType {NORMAL, FIRE, WATER, GRASS, ELECTRIC, ICE, ROCK, FAIRY, DRAGON, STEEL, FIGHTING, POISON, FLYING, PSYCHIC, GROUND, BUG, GHOST, DARK}
enum PokeStat {HEALTH, ATTACK, DEFENSE, SPECIAL_ATTACK, SPECIAL_DEFENSE, SPEED}
const poke_type_names: Array[String] = ["normal", "fire", "water", "grass", "electric", "ice", "rock", "fairy", "dragon", "steel", "fighting", "poison", "flying", "psychic", "ground", "bug", "ghost", "dark"]
const poke_stat_names: Array[String] = ["health", "attack", "defense", "special attack", "special defense", "speed"]
const poke_types_in_pokedex: Dictionary = {"hp": PokeStat.HEALTH, "atk": PokeStat.ATTACK, "def": PokeStat.DEFENSE, "spa": PokeStat.SPECIAL_ATTACK, "spd": PokeStat.SPECIAL_DEFENSE, "spe": PokeStat.SPEED}
static func stat_from_name(name: String) -> PokeStat:
	return poke_type_names.find(name) as PokeStat
static func type_from_name(name: String) -> PokeType:
	return poke_stat_names.find(name) as PokeType
	
static var non_alpha_num_regex: RegEx = null
static func normalize_name(name: String) -> String:
	if not non_alpha_num_regex:
		non_alpha_num_regex = RegEx.new()
		non_alpha_num_regex.compile("[^a-z0-9]")
	return non_alpha_num_regex.sub(name.to_lower(), "", true)
const regions: Array[String] = ["alola", "galar", "paldea", "hisui"]
const POKEMON_IMAGE_PATH: String = "res://Media/Images/Pokemon"

class Config extends RefCounted:
	var types : Array[PokeType]
	var type_colors : Dictionary
	var type_effectiveness : Array[Array]
	var stats : Array[PokeStat]
	var elo_gradient: Gradient
	
	func _init( 
		types : Array[String],
		type_colors : Dictionary, 
		type_effectiveness : Array[Array],
		stats : Array[String],
		elo_gradient: Dictionary):
		
		self.types = types.map(PokemonLib.type_from_name)
		self.type_colors = type_colors
		self.type_effectiveness = type_effectiveness
		self.stats = stats.map(PokemonLib.stat_from_name)
		self.elo_gradient = MathLib.parse_gradient(elo_gradient)

	static func from_dict(data : Dictionary) -> Config:
		return Config.new(data["types"], data["type_colors"], data["type_effectiveness"], data["stats"], data["elo_gradient"])	

static var _config: Config = null
static func get_config() -> Config:
	if _config:
		return _config
	var file = FileAccess.open("res://Config/config.json", FileAccess.READ)
	var file_contents = file.get_as_text()
	var data = JSON.parse_string(file_contents)
	_config = Config.from_dict(data)
	return _config

class Pokemon extends RefCounted:
	# A normalized name containing only alphanumeric
	var id: String
	# The numeric Pokedex id of the pokemon
	var num: int
	# The stylized English name of the pokemon
	var name: String
	# The type(s) of the pokemon
	var types: Array[String]
	# Dictionary linking stat names to their base value
	var base_stats: Array[int]
	# Strings normalized by `normalize_name` of the starting ability values
	var abilities: Array[String]
	# The height in meters
	var heightm: float
	# The weight in kilograms
	var weightkg: float
	# A descriptive single color for the pokemon
	var color: String
	# The specific gender of this pokemon, if forced to be one (M,F) or is genderless (N), otherwise this is empty
	var gender: String
	# Any special forms that apply to this variant
	var formes: Array[String]
	# Any other pokemon that this pokemon can evolve into
	var evos: Array[String]
	# A pokemon (if any) that this pokenon evolves from
	var prevo: String
	# The type of evolution that this pokemon has (e.g. level, levelFriendship, useItem, trade, other...)
	var evo_type: String
	# The condition (if any) for this pokemon to evolve
	var evo_condition: String
	# The level required for this pokemon to evolve. -1 if unknown or no level is required
	var evo_level: int 
	# The egg groups that this pokemon falls into
	var egg_groups: Array[String]
	# Competitive tier of the pokemon
	var tier: String
	
	var is_regional: bool = false
	var is_mega: bool = false
	var is_totem: bool = false
	var is_base: bool = false
	var alt_types: bool = false
	var misc_variant: bool = false
	var image_filename: String = ""
	var image: ImageTexture = null
	
	func _init( 
		id: String, num: int, name: String, types: Array[String],
		base_stats: Dictionary = {}, abilities: Dictionary = {},
		heightm: float = -1, weightkg: float = -1, color: String = "", gender: String = "", forme: String = "",
		evos: Array[String] = [], prevo: String = "", evo_type: String = "level", evo_condition: String = "", evo_level: int = -1, 
		egg_groups: Array[String] = [], tier: String = ""):
		
		self.id = id
		self.num = num
		self.name = name
		self.types = types.map(PokemonLib.normalize_name)
		self.base_stats = []
		for i in PokeStat.values():
			self.base_stats.append(-1)
		if len(base_stats) != len(PokeStat):
			print_debug("Received improperly sized dictionary for pokemon %s, expecting %d values." % [self.id, len(PokeStat)], base_stats)
		for t in base_stats:
			if t not in poke_types_in_pokedex:
				print_debug("Failed to recognize stat for pokemeon %s: \"%s\"" % [self.id, t])
			self.base_stats[poke_types_in_pokedex[t]] = base_stats[t]
		
		self.abilities = abilities.values().map(PokemonLib.normalize_name)
		self.height = heightm
		self.weight = weightkg
		self.color = color 
		self.evolutions = evos
		self.preevolution = prevo
		self.evolution_type = evo_type
		self.evolution_condition = evo_condition
		self.evolution_level = evo_level
		self.gender = gender
		self.egg_groups = egg_groups
		self.tier = tier
		self.formes = ArrayUtils.packed_string_array_map(forme.split("-", false), func(s:String): s.to_lower())

		# Postprocessing variables
		self.is_regional = false
		for r in regions:
			if r in self.formes:
				self.region = r
				self.is_regional = true
				break
		# self.starter = "starter" in self.formes
		self.is_mega = "mega" in self.formes
		self.is_gmax = "gmax" in self.formes
		self.is_totem = "totem" in self.formes
		self.is_base = (self.formes == []) and (self.num > 0)

		self.alt_types = false
		self.misc_variant = not (self.is_base or self.is_regional or self.is_mega or self.is_gmax or self.is_totem)

		self.image_filename = "%04d_%s.png" % [self.num, self.id]
		self.image_path = "%s/%s" % [POKEMON_IMAGE_PATH, self.image_filename]
		
	func get_image() -> ImageTexture:
		if self.image == null and FileAccess.file_exists(self.img_path):
			var image = Image.new()
			image.load(self.image_path)
			var texture = ImageTexture.new()
			texture.create_from_image(image)
			self.image = texture
		return self.image
	
	static func from_dict(pokemon_id: String, data: Dictionary) -> Pokemon:
		return Pokemon.new(pokemon_id, data["num"], data["name"], data["types"], 
			data.get("baseStats", {}), data.get("abilities", {}), 
			data.get("heightm", -1), data.get("weightkg", -1), data.get("color", ""), data.get("gender", ""), data.get("forme", ""),
			data.get("evos", []), data.get("prevo", ""), data.get("evoTypes", "level"), data.get("evoCondition", ""), data.get("evoLevel", -1),
			data.get("groups", []), data.get("tier", "")
		)

static var _pokedex: Array[Pokemon] = []
static func get_pokedex() -> Array[Pokemon]:
	if not _pokedex.is_empty():
		return _pokedex
	var file = FileAccess.open("res://Config/pokedex.json", FileAccess.READ)
	var file_contents = file.get_as_text()
	var data = JSON.parse_string(file_contents)
	_pokedex = data.map(Pokemon.from_dict)
	return _pokedex
