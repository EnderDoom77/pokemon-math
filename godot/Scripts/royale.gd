class_name Royale
extends Control

const DEFAULT_ELO = 500
const DEFAULT_K = 400
const DEFAULT_K_DECAY = 0.975
const MIN_ELO = 0
const MIN_K = 0

# weighting constants
const ELO_WEIGHT_EXPONENT = 1.25
const K_WEIGHT_EXPONENT = 1.1
const ELO_DELTA_WEIGHT_EXPONENT = 1.5

@export var left_display: PokemonDisplay
@export var right_display: PokemonDisplay
@export var left_elo_delta: FadingTextDisplay
@export var right_elo_delta: FadingTextDisplay

@export var negative_color: Color
@export var neutral_color: Color
@export var positive_color: Color

var session: SessionManager = SessionManager.get_singleton()

# Called when the node enters the scene tree for the first time.
func _ready():
	SessionManager.get_singleton().on_save_changed.connect(_on_save_changed)
	fetch_pokemon_pair()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass

# EVENTS
func _on_rating_buttons_evaluated(score: float):
	var score_left = -score
	var score_right = score
	var elo_left = get_elo_info(get_left().id).elo
	var elo_right = get_elo_info(get_right().id).elo
	evaluate_left(score_left, elo_right)
	evaluate_right(score_right, elo_left)
	fetch_pokemon_pair()
	
func _on_left_pokemon_evaluated(score: float):
	evaluate_right(score, DEFAULT_ELO)
	fetch_pokemon_pair()
	
func _on_right_pokemon_evaluated(score: float):
	evaluate_left(score, DEFAULT_ELO)
	fetch_pokemon_pair()

func _on_save_changed(_data: SaveManager.SaveData):
	fetch_pokemon_pair()

# LOGIC
const MAX_FETCH_DEPTH = 100
func fetch_pokemon_pair(depth: int = 0):
	var eligible_list: Array[String] = session.current_save.eligible_pokemon
	var pokedex = PokemonLib.get_pokedex()
	if depth > MAX_FETCH_DEPTH:
		var pair = MathLib.random_pair(eligible_list)
		set_left(pokedex[pair.first])
		set_right(pokedex[pair.second])
	var left_weights: Array[float] = []
	left_weights.assign(eligible_list.map(get_pokemon_weight_left))
	var left_id = MathLib.random_sample_weighted(eligible_list, left_weights)
	var left_elo = get_elo_info(left_id).elo
	
	var any_opponent_eligible = false
	var right_weights: Array[float] = []
	for pokemon_id in eligible_list:
		var w = get_pokemon_weight_right(pokemon_id, left_elo, left_id)
		right_weights.append(w)
		if w > 0: 
			any_opponent_eligible = true
	if not any_opponent_eligible:
		fetch_pokemon_pair(depth + 1)
		return
	var right_id = MathLib.random_sample_weighted(eligible_list, right_weights)
	set_left(pokedex[left_id])
	set_right(pokedex[right_id])
	SaveManager.save()

func get_pokemon_weight_left(pokemon_id: String):
	var elo_info = get_elo_info(pokemon_id)
	var w = 1
	if elo_info.k == DEFAULT_K:
		w *= 5
	if elo_info.elo == MIN_ELO:
		w *= 0.25
	
	return w * pow(elo_info.elo, ELO_WEIGHT_EXPONENT) * pow(elo_info.k, K_WEIGHT_EXPONENT)

const MAX_ELO_DELTA = 400
func get_pokemon_weight_right(pokemon_id: String, other_elo: float, other_id: String):
	if pokemon_id == other_id: return 0
	var elo_info = get_elo_info(pokemon_id)
	var elo_delta = abs(elo_info.elo - other_elo)
	return max(0, pow(1 - elo_delta / MAX_ELO_DELTA, ELO_DELTA_WEIGHT_EXPONENT))
	
func get_left() -> PokemonLib.Pokemon:
	return left_display.pokemon
func get_right() -> PokemonLib.Pokemon:
	return right_display.pokemon
func set_left(pokemon: PokemonLib.Pokemon):
	left_display.set_pokemon(pokemon)
func set_right(pokemon: PokemonLib.Pokemon):
	right_display.set_pokemon(pokemon)

func get_color_from_sign(x: float) -> Color:
	return MathLib.value_by_signum(x, negative_color, neutral_color, positive_color)

func evaluate_left(score: float, opponent_elo: float):
	var elo_delta = evaluate_pokemon(get_left(), score, opponent_elo)
	left_elo_delta.show_text("(%s)" % MathLib.signed(elo_delta, "%d"), 2, get_color_from_sign(elo_delta))
	
func evaluate_right(score: float, opponent_elo: float):
	var elo_delta = evaluate_pokemon(get_right(), score, opponent_elo)
	right_elo_delta.show_text("(%s)" % MathLib.signed(elo_delta, "%d"), 2, get_color_from_sign(elo_delta))
	
## Evaluates a pokemon, updates their elo info, and returns the elo delta
func evaluate_pokemon(target: PokemonLib.Pokemon, score: float, opponent_elo: float) -> float:
	var normalized_score = (score + 1) / 2
	var elo_info = get_elo_info(target.id)
	var elo_delta = MathLib.calc_elo_delta(elo_info.elo, opponent_elo, elo_info.k, normalized_score)
	update_elo(target.id, elo_info.elo + elo_delta)
	return elo_delta	
	
func get_elo_info(pokemon_id: String) -> SaveManager.PokeEloData:
	return session.current_save.get_info(pokemon_id)
func update_elo(pokemon_id: String, new_elo: float, k_decay = DEFAULT_K_DECAY, save_immediately: bool = false) -> void:
	var elo_info = session.current_save.elo_info[pokemon_id]
	elo_info.elo = max(MIN_ELO, new_elo)
	elo_info.k = max(MIN_K, elo_info.k * k_decay)
	if save_immediately:
		session.current_save.save()
	
