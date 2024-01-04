class_name EloInfoDisplay
extends HBoxContainer

@export var positive_color: Color
@export var neutral_color: Color
@export var negative_color: Color

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass
	
func set_values(values: SaveManager.PokeEloData):
	var elo_gradient: Gradient = PokemonLib.get_config().elo_gradient
	var elo = values.elo
	$EloDisplay.text = "%d" % elo
	$EloDisplay.self_modulate = elo_gradient.sample(elo)
	
	var elo_delta = values.elo_delta()
	$EloDeltaDisplay.text = "(%s)" % MathLib.signed(elo_delta, "%d")
	$EloDeltaDisplay.self_modulate = MathLib.value_by_signum(elo_delta, negative_color, neutral_color, positive_color)
	
