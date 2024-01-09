class_name RatingButtonManager
extends Panel

@export
var button_prefab: PackedScene
@export
var scores: Array[float]
@export
var color_left: Color
@export
var color_neutral: Color
@export
var color_right: Color

signal evaluated(score: float)

func color_from_score(score: float) -> Color:
	if score < 0:
		return color_neutral.lerp(color_left, -score)
	else:
		return color_neutral.lerp(color_right, score)

# Called when the node enters the scene tree for the first time.
func _ready():
	var container: Container = $MarginContainer/HBoxContainer
	
	for score in scores:
		var new_btn: Button = button_prefab.instantiate()
		new_btn.set_text(MathLib.signed(score, "%.1f"))
		create_rating_button_stylebox(new_btn, score)
		container.add_child(new_btn)
		print_debug("Added button for score %.1f" % score)
		
		new_btn.pressed.connect(func(): evaluate(score))
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass

func evaluate(score):
	print("Evaluating with score %.1f" % score)
	evaluated.emit(score)
	
func create_rating_button_stylebox(btn: Button, score: float):
	var base_color = color_from_score(score)
	var dict = {"normal": 0, "hover": 0.2, "active": 0, "pressed": 0.4}
	for style_name in dict:
		var lightness = dict[style_name]
		var style_box: StyleBoxFlat = btn.get_theme_stylebox(style_name).duplicate()
		style_box.bg_color = base_color.lightened(lightness)
		btn.add_theme_stylebox_override(style_name, style_box)
		
	
	
