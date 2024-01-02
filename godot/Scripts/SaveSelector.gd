extends OptionButton

var savenames: Array[String] = []
var notify: bool = true

@export var new_dialog: Node
@export var new_button: Button
@export var confirm_button: Button
@export var savename_input: LineEdit
@export var confirmation_dialog: ConfirmationDialog

@export var icon_new: Texture2D
@export var icon_cancel: Texture2D

# Called when the node enters the scene tree for the first time.
func _ready():
	for savename in SaveManager.get_all_saves().map(FileUtils.get_filename):
		add_save(savename)
	self.item_selected.connect(on_item_selected)
	var current_savename = SessionManager.get_singleton().current_save.savename
	select_save(current_savename, false)

func add_save(savename: String) -> void:
	self.add_item(savename)
	savenames.append(savename)

func select_save(savename: String, notify: bool = false) -> void:
	var idx = self.savenames.find(savename)
	self.notify = notify
	self.select(savenames.find(savename))	
	self.notify = true
	
func remove_save(savename: String) -> bool:
	var idx = self.savenames.find(savename)
	if idx < 0: return false
	self.remove_item(idx)
	return true

func on_item_selected(idx: int):
	var savename = self.savenames[idx]
	var session = SessionManager.get_singleton()
	session.change_savefile(savename, notify)

func _on_new_toggled(toggled_on: bool):
	new_dialog.visible = toggled_on
	confirm_button.disabled = not SaveManager.is_savename_valid(name)
	new_button.icon = icon_cancel if toggled_on else icon_new

func _on_confirm_pressed():
	var name = savename_input.text
	if SaveManager.is_savename_valid(name): 
		SaveManager.create_save(name)
		add_save(name)
		SessionManager.get_singleton().change_savefile(name)
		select_save(name, false)
		new_button.button_pressed = false
		_on_new_toggled(false)

func _on_line_edit_text_changed(new_text: String):
	confirm_button.disabled = not SaveManager.is_savename_valid(name)

func _on_delete_pressed():
	confirmation_dialog.popup()

func _on_confirmation_dialog_confirmed():
	var session = SessionManager.get_singleton()
	var current_save = session.current_save.savename
	SaveManager.delete_save(current_save)
	select_save(session.current_save.savename)
	remove_save(current_save)
