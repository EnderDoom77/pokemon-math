class_name ArrayUtils

extends Object

static func dictionary_map(array: Array[Variant], dict: Dictionary) -> Array[Variant]:
	var result = []
	for value in array:
		result.append(dict[value])
	return result
	
static func dictionary_map_safe(array: Array[Variant], dict: Dictionary, default: Variant) -> Array[Variant]:
	var result = []
	for value in array:
		result.append(dict.get(value, default))
	return result
	
static func packed_string_array_map(string_array: PackedStringArray, function: Callable) -> Array[String]:
	var result = []
	for s in string_array:
		result.append(function.call(s))
	return result
	
static func arg_max(array: Array[Variant], key: Callable) -> Variant:
	if array.is_empty(): return null
	var max_value = key.call(array[0])
	var max_arg = array[0]
	for i in range(1,len(array)):
		var new_value = key.call(array[i])
		if new_value > max_value:
			max_value = new_value
			max_arg = array[i]
	return max_arg
