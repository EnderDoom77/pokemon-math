extends MarginContainer

@export
var current_screen: String
@export
var screens_container: Node

var screens: Dictionary

func _ready():
	for child in screens_container.get_children():
		screens[child.name] = child
		child.set_process(false)
		child.visible = false
	switch_screen(current_screen)

func _process(_delta):
	pass

func switch_screen(screen_name: String):
	screens[current_screen].visible = false
	screens[current_screen].set_process(false)
	current_screen = screen_name
	screens[current_screen].visible = true
	screens[current_screen].set_process(true)

func _on_royale_pressed():
	switch_screen("Royale")
	
func _on_leaderboard_pressed():
	switch_screen("Leaderboard")
