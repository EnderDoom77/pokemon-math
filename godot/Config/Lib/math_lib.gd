class_name MathLib
extends Object

static func parse_gradient(key_value_pairs: Dictionary) -> Gradient:
	var keys = key_value_pairs.keys()
	keys.sort()
	var values = ArrayUtils.dictionary_map(keys, key_value_pairs)
	var gradient: Gradient = Gradient.new()
	gradient.offsets = keys
	gradient.colors = values
	return gradient		

static func sum(x: Array):
	var r = 0
	for v in x:
		r += v
	return r

static func prod(x: Array):
	var r = 1
	for v in x:
		r *= v
	return r
	
static func clamp01(x: float) -> float:
	if x < 0: return 0
	if x > 1: return 1
	return x

static func signed(x: float, fmt: String = "%f") -> String:
	return ('+' if x > 0 else '') + (fmt % x)

static func value_by_signum(v: float, if_negative: Variant, if_neutral: Variant, if_positive: Variant):
	if v == 0:
		return if_neutral
	if v < 0:
		return if_negative
	else:
		return if_positive

static func random_sample(values: Array[Variant]) -> Variant:
	assert(len(values) > 0, "You may not sample an empty array")
	var idx = randi_range(0, len(values) - 1)
	return values[idx]

static func random_index_weighted(weights: Array[float]) -> int:
	var count = len(weights)
	assert(count > 0, "You may not sample an empty array")
	var total_weight = sum(weights)
	var target_weight = randf_range(0, total_weight)
	var running_weight = 0
	for i in count:
		running_weight += weights[i]
		if running_weight > target_weight:
			return i
	return len(weights) - 1

static func random_sample_weighted(values: Array[Variant], weights: Array[float]) -> Variant:
	var count = len(values)
	assert(count == len(weights), "The length of values and weights passed to a weighted random sample must be the same, received %d values and %d weights" % [len(values), len(weights)])
	var idx = random_index_weighted(weights)
	return values[idx]

class Pair:
	var first: Variant
	var second: Variant
	func _init(first_val: Variant, second_val: Variant):
		first = first_val
		second = second_val

static func random_pair(values: Array[Variant]) -> Pair:
	var count = len(values)
	assert(count >= 2, "The length of the array must be at least 2 to fetch a pair from the array, received %s" % values)
	var first_idx = randi_range(0, len(values) - 1)
	var second_idx = randi_range(0, len(values) - 2)
	if (second_idx >= first_idx): second_idx += 1
	return Pair.new(values[first_idx], values[second_idx])

const REL_LUM_THRESHOLD = 0.03928
const REL_LUM_DIVISOR = 12.92
static func _rel_luminance_preprocess_component(x: float):
	return x/REL_LUM_DIVISOR if x <= REL_LUM_THRESHOLD else pow((x+0.055)/1.055, 2.4)

static func rel_luminance(color: Color) -> float:
	var r = _rel_luminance_preprocess_component(color.r)
	var g = _rel_luminance_preprocess_component(color.g)
	var b = _rel_luminance_preprocess_component(color.b)
	return 0.2126 * r + 0.7152 * g + 0.0722 * b

static func contrast(bg: Color, fg: Color) -> float:
	"""
	Returns a value from 1 to 21 indicating the contrast quality between a background color and a background color
	"""
	var l1 = rel_luminance(bg)
	var l2 = rel_luminance(fg)
	return max((l1+0.05)/(l2+0.05), (l2+0.05)/(l1+0.05))

static func max_contrast(color: Color, tint: float = 0) -> Color:
	"""
	Returns a color with high contrast and the same hue as the original color.
	`tint` is a value from 0 to 1 which indicates how much of the hue and saturation should be maintained, at the cost of contrast.
	"""
	var hue = color.h
	var sat = color.s
	var alpha = color.a
	var lightness_options = [tint * 50, (2 - tint) * 50]
	var resulting_colors = lightness_options.map(func(l): return Color.from_ok_hsl(hue, sat, l, alpha))
	return ArrayUtils.arg_max(resulting_colors, func(c): return contrast(color, c))

static func calc_elo_delta(own_elo: float, opponent_elo: float, k_value: float, result_score: float) -> float:
	var q_own = pow(10, own_elo/400.0)
	var q_opponent = pow(10, opponent_elo/400.0)
	
	var expected_score = q_own/(q_own + q_opponent)
	return k_value * (result_score - expected_score)
	
class CustomGradient:
	var keys: Array[float]
	var values: Array[Color]
	
	@warning_ignore("shadowed_variable")
	func _init(keys: Array[float], values: Array[Color]):
		self.keys = keys
		self.values = values
	
	func eval(t: float) -> Color:
		var left_k = keys[0]
		var left_v = values[0]
		for k in self.keys:
			var v = values[k]
			if t < k:
				return left_v.lerp(v, (t - left_k)/(k - left_k))
			left_k = k
			left_v = v
		return left_v
	
class Set extends RefCounted:
	var _internal_dict: Dictionary
	
	func _init(contents: Array = []):
		add_range(contents)
	static func from_dictionary_keys(dictionary: Dictionary) -> Set:
		var result = Set.new()
		result._internal_dict = dictionary.duplicate()
		return result
	func contains(x: Variant) -> bool:
		return x in _internal_dict
	func add(x: Variant):
		_internal_dict[x] = true
	func remove(x: Variant):
		_internal_dict.erase(x)
	func add_range(x: Array):
		for key in x:
			add(key)
	func remove_range(x: Array):
		for key in x:
			remove(key)
	func union_with(other_set: Set):
		_internal_dict.merge(other_set._internal_dict)
	static func union(set_a: Set, set_b: Set) -> Set:
		var result = Set.from_dictionary_keys(set_a._internal_dict)
		result.union_with(set_b)
		return result
