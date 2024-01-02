class_name SessionManager
extends RefCounted

signal on_save_changed(new_save: SaveManager.SaveData)

const DEFAULT_SESSION_PATH = "user://session.json"
const DEFAULT_SAVENAME = "default"

class Session:
	var savename: String
	@warning_ignore("shadowed_variable")
	func _init(savename: String):
		self.savename = savename

	func save(path: String = DEFAULT_SESSION_PATH):
		FileUtils.save_json(path, {
			"savename": self.savename
		})

	static func from_dict(data: Dictionary) -> Session:
		return Session.new(data.get("savename", DEFAULT_SAVENAME))

	static func from_path(path: String = DEFAULT_SESSION_PATH) -> Session:
		return Session.from_dict(FileUtils.get_or_create_json_data_file(path, {}))

static var _instance: SessionManager = null
static func get_singleton() -> SessionManager:
	if _instance: return _instance
	_instance = SessionManager.new()
	return _instance 

var current_session: Session = Session.from_path()
var current_save: SaveManager.SaveData = SaveManager.SaveData.from_name(current_session.savename)

func change_savefile(new_name: String, notify: bool = false) -> SaveManager.SaveData:
	current_session.savename = new_name
	current_session.save()
	current_save = SaveManager.SaveData.from_name(new_name)
	if notify:
		on_save_changed.emit(current_save)
	return current_save
