class_name SaveManager
extends Object

const SAVEFILE_PATH = "user://saves"

static func get_all_saves():
	var result = []
	for path in FileUtils.get_files_in_dir(SAVEFILE_PATH):
		result.append(FileUtils.get_filename(path))
	return result

static func create_save(savename: String) -> SaveData:
	return SaveData.from_name(savename)

static func delete_save(savename: String):
	SaveData.delete(savename)
	SessionManager.get_singleton().change_savefile(SessionManager.DEFAULT_SAVENAME)

static func is_savename_valid(savename: String) -> bool:
	return savename.is_valid_filename() and len(savename) > 0

class SaveData extends RefCounted:
	var savename: String = ""
	## a dictionary connecting pokemon IDs to PokeEloData
	var elo_info: Dictionary = {}
	const SAVEFILE_FORMAT: String = SAVEFILE_PATH + "/%s.json"
	
	@warning_ignore("shadowed_variable")
	func _init(savename, eligible_pokemon: Array[String] = []):
		self.savename = savename
		for p:String in eligible_pokemon:
			elo_info[p] = PokeEloData.new()
	
	static func from_dict(savename, data: Dictionary) -> SaveData:
		var result = SaveData.new(savename)
		for k:String in data.get("elo_info", {}).keys():
			var poke_data = PokeEloData.from_dict(data[k])
			result.elo_info[k] = poke_data
		return result
		
	static func from_path(path: String) -> SaveData:
		return SaveData.from_dict(
			FileUtils.get_filename(path),
			FileUtils.get_or_create_json_data_file(path, {})
		)
		
	static func from_name(savename: String) -> SaveData:
		return SaveData.from_path(SAVEFILE_FORMAT % savename)
	
	static func delete(savename: String) -> Error:
		var err = DirAccess.remove_absolute(SAVEFILE_FORMAT % savename)
		return err
	
	func to_dict() -> Dictionary:
		return {
			"elo_info": self.elo_info
		}
	
	func save_to_path(path: String) -> void:
		FileUtils.save_json(path, self.to_dict())
		
	func save():
		save_to_path(SAVEFILE_FORMAT % self.savename)
	
class PokeEloData extends RefCounted:
	var elo: float
	var k: float
	
	@warning_ignore("shadowed_variable")
	func _init(elo: float = Royale.DEFAULT_ELO, k: float = Royale.DEFAULT_K):
		self.elo = elo
		self.k = k
	
	func to_dict() -> Dictionary:
		return {
			"elo": self.elo,
			"k": self.k
		}
	
	static func from_dict(data: Dictionary) -> PokeEloData:
		return PokeEloData.new(data.get("elo", Royale.DEFAULT_ELO), data.get("k", Royale.DEFAULT_K))
