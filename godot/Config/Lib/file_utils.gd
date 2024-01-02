class_name FileUtils
extends Object

static func get_or_create_json_data_file(path: String, default: Variant) -> Variant:
	var file: FileAccess
	var data: Variant
	if not FileAccess.file_exists(path):
		# Create a new file in that path
		FileUtils.save_json(path, default)
		return default
	file = FileAccess.open(path, FileAccess.READ)
	data = JSON.parse_string(file.get_as_text())
	file.close()
	return data

static func save_json(path: String, data: Variant) -> void:
	var res = DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	if res != OK:
		push_error("Failed to create directory tree up to %s, got error %s" % [path, res]) 
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "\t"))
	file.close()

static func get_files_in_dir(path: String, recursive: bool = true) -> Array[String]:
	var result: Array[String] = []
	var dir = DirAccess.open(path)
	if dir:
		dir.list_dir_begin()
		var filename = dir.get_next()
		while filename:
			var filepath = path.path_join(filename)
			if not dir.current_is_dir():
				result.append(filepath)
			elif recursive:
				result.append_array(FileUtils.get_files_in_dir(filepath, recursive))
			filename = dir.get_next()
	return result

static func get_filename(path: String) -> String:
	return path.get_file().get_basename()
