class_name SaveManager
extends Object

const SAVEFILE_PATH = "user://saves"

static func get_all_saves():
	var result = []
	for path in FileUtils.get_files_in_dir(SAVEFILE_PATH):
		result.append(FileUtils.get_filename(path))
	return result

static func save():
	SessionManager.get_singleton().current_save.save()

static func create_save(savename: String) -> SaveData:
	return SaveData.from_name(savename)

static func delete_save(savename: String):
	SaveData.delete(savename)
	SessionManager.get_singleton().change_savefile(SessionManager.DEFAULT_SAVENAME)

static func is_savename_valid(savename: String) -> bool:
	return savename.is_valid_filename() and len(savename) > 0

class SaveData extends RefCounted:
	var savename: String = ""
	var eligible_pokemon: Array[String]
	## a dictionary connecting pokemon IDs to PokeEloData
	var elo_info: Dictionary = {}
	const SAVEFILE_FORMAT: String = SAVEFILE_PATH + "/%s.json"
	
	@warning_ignore("shadowed_variable")
	func _init(savename, eligible_pokemon: Array[String] = []):
		self.savename = savename
		if not eligible_pokemon:
			self.eligible_pokemon.assign(PokemonLib.get_default_eligible_pokemon().map(func(p): return p.id))
		else:
			self.eligible_pokemon.assign(eligible_pokemon)
			
		for p:String in eligible_pokemon:
			elo_info[p] = PokeEloData.new()
	
	func get_savepath() -> String:
		return SAVEFILE_FORMAT % savename
		
	func get_info(pokemon_id: String) -> PokeEloData:
		if pokemon_id not in elo_info:
			elo_info[pokemon_id] = PokeEloData.new()
		return elo_info[pokemon_id]
		
	@warning_ignore("shadowed_variable")
	static func get_savepath_by_name(savename: String) -> String:
		return SAVEFILE_FORMAT % savename
	
	@warning_ignore("shadowed_variable")
	static func from_dict(savename, data: Dictionary) -> SaveData:
		var eligible_pokemon: Array[String] = []
		eligible_pokemon.assign(data.get("eligible_pokemon", []))
		var result = SaveData.new(savename, eligible_pokemon)
		for k:String in data.get("elo_info", {}).keys():
			var poke_data = PokeEloData.from_dict(data["elo_info"][k])
			result.elo_info[k] = poke_data
		return result
		
	static func from_path(path: String) -> SaveData:
		return SaveData.from_dict(
			FileUtils.get_filename(path),
			FileUtils.get_or_create_json_data_file(path, {})
		)
		
	@warning_ignore("shadowed_variable")
	static func from_name(savename: String) -> SaveData:
		return SaveData.from_path(get_savepath_by_name(savename))
	
	@warning_ignore("shadowed_variable")
	static func delete(savename: String) -> Error:
		var err = DirAccess.remove_absolute(get_savepath_by_name(savename))
		return err
	
	func to_dict() -> Dictionary:
		var result = {
			"elo_info": {}, 
			"eligible_pokemon": self.eligible_pokemon
		}
		for v: String in elo_info:
			var elo_data: PokeEloData = elo_info[v]
			result["elo_info"][v] = elo_data.to_dict()
		return result
	
	func save_to_path(path: String) -> void:
		FileUtils.save_json(path, self.to_dict())
		
	func save():
		save_to_path(get_savepath())
	
class PokeEloData extends RefCounted:
	var elo: float
	var k: float
	var elo_original: float
	
	@warning_ignore("shadowed_variable")
	func _init(elo: float = Royale.DEFAULT_ELO, k: float = Royale.DEFAULT_K):
		self.elo = elo
		self.k = k
		self.elo_original = elo
	
	func to_dict() -> Dictionary:
		return {
			"elo": self.elo,
			"k": self.k
		}
	
	## Gets the difference of elo from the current value to the value the last time it was loaded
	func elo_delta() -> float:
		return elo - elo_original
	
	static func from_dict(data: Dictionary) -> PokeEloData:
		return PokeEloData.new(data.get("elo", Royale.DEFAULT_ELO), data.get("k", Royale.DEFAULT_K))
