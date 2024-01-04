class_name FadingTextDisplay

extends Label

# Called when the node enters the scene tree for the first time.
func _ready():
	pass
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(_delta):
	pass
	
func show_text(shown_text: String = "", time: float = -1, color: Color = Color.WHITE):
	self.text = shown_text
	self.self_modulate = color
	if time <= 0: return
	var tween = create_tween().set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_CUBIC)
	tween.tween_property(self, "self_modulate:a", 0, time).from(1)	
