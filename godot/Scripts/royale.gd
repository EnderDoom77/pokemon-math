class_name Royale
extends Control

const DEFAULT_ELO = 500
const DEFAULT_K = 400
const DEFAULT_K_DECAY = 0.975
const MIN_ELO = 0
const MIN_K = 0

@export var left_display: PokemonDisplay
@export var right_display: PokemonDisplay

var session: SessionManager = SessionManager.get_singleton()

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

# EVENTS
func _on_rating_buttons_evaluated(score: float):
	var score_left = -score
	var score_right = score
	var elo_left = get_elo_info(get_left().id).elo
	var elo_right = get_elo_info(get_right().id).elo
	evaluate_left(score_left, elo_right)
	evaluate_right(score_right, elo_left)
func _on_left_pokemon_evaluated(score: float):
	evaluate_right(score, DEFAULT_ELO)
func _on_right_pokemon_evaluated(score: float):
	evaluate_left(score, DEFAULT_ELO)

# LOGIC
func get_left() -> PokemonLib.Pokemon:
	return left_display.pokemon
func get_right() -> PokemonLib.Pokemon:
	return right_display.pokemon

func evaluate_left(score: float, opponent_elo: float):
	pass
	
func evaluate_right(score: float, opponent_elo: float):
	pass
	
func get_elo_info(pokemon_id: String) -> SaveManager.PokeEloData:
	return session.current_save.elo_info[pokemon_id]
func update_elo(pokemon_id: String, new_elo: float, k_decay = DEFAULT_K_DECAY, save_immediately: bool = false) -> void:
	var elo_info = session.current_save.elo_info[pokemon_id]
	elo_info.elo = max(MIN_ELO, new_elo)
	elo_info.k = max(MIN_K, elo_info.k * k_decay)
	
