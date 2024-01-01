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

static func prod(x: Array):
	var r = 1
	for v in x:
		r *= v
	return r
	
static func clamp01(x: float) -> float:
	if x < 0: return 0
	if x > 1: return 1
	return x

static func signed(x: float) -> String:
	return ('+' if x > 0 else '') + str(x)

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

static func calc_elo_delta(own_elo: int, opponent_elo: int, k_value: float, result_score: float) -> int:
	var q_own = pow(10, own_elo/400.0)
	var q_opponent = pow(10, opponent_elo/400.0)
	
	var expected_score = q_own/(q_own + q_opponent)
	return int(k_value * (result_score - expected_score))
	
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
