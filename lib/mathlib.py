from typing import Generic, TypeVar
import colorsys
import math
from pygame import Color

def prod(x):
    r = 1
    for v in x:
        r *= v
    return r

def clamp01(x):
    if x < 0: return 0
    if x > 1: return 1
    return x

def signed(x) -> str:
    return f"{'+' if x > 0 else ''}{x}"

def lerp(left: tuple | list, right: tuple | list, t: float) -> tuple:
    return tuple([l + (r-l)*t for l,r in zip(left, right)])

REL_LUM_THRESHOLD = 0.03928
REL_LUM_DIVISOR = 12.92
def _rel_luminance_preprocess_component(x: float):
    return x/REL_LUM_DIVISOR if x <= REL_LUM_THRESHOLD else math.pow((x+0.055)/1.055, 2.4)

def rel_luminance(r: float, g: float, b: float, *, rgb_range:float = 1) -> float:
    r,g,b = r/rgb_range, g/rgb_range, b/rgb_range
    r = _rel_luminance_preprocess_component(r)
    g = _rel_luminance_preprocess_component(g)
    b = _rel_luminance_preprocess_component(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(bg: Color, fg: Color) -> float:
    """
    Returns a value from 1 to 21 indicating the contrast quality between a background color and a background color
    """
    l1, l2 = tuple(sorted((rel_luminance(r,g,b, rgb_range=255) for r,g,b,*_ in (bg,fg)), reverse=True))
    return (l1+0.05)/(l2+0.05)

def max_contrast(color: Color, tint: float = 0) -> Color:
    """
    Returns a color with high contrast and the same hue as the original color.
    `tint` is a value from 0 to 1 which indicates how much of the hue and saturation should be maintained, at the cost of contrast.
    """
    color = Color(color)
    hue,sat,_,alpha = color.hsla
    lightness_options = [tint * 50, (2 - tint) * 50]
    resulting_colors = [(*hsl2rgb((hue,sat,l), convert_from_pygame=True), alpha/100 * UNIT_TO_PYGAME) for l in lightness_options]
    contrast_values = [contrast(color, c) for c in resulting_colors]
    best_contrast, best_color = max(zip(contrast_values, resulting_colors))
    return best_color

def calc_elo_delta(own_elo: int, opponent_elo: int, k_value: float, result_score: float) -> int:
    q_own = math.pow(10, own_elo/400)
    q_opponent = math.pow(10, opponent_elo/400)
    
    expected_score = q_own/(q_own + q_opponent)
    return int(k_value * (result_score - expected_score))


UNIT_TO_PYGAME = (256.0 - 1e-6)
def convert_pygame_polarcolor_to_units(h,s,v_or_l,a=100):
    return (h/360, s/100, v_or_l/100, a/100)

def hsl2rgb(hsl: tuple[float,float,float], convert_from_pygame: bool = False) -> tuple[int,int,int]:
    h,s,l,*_ = hsl
    if convert_from_pygame:
        h,s,l,_ = convert_pygame_polarcolor_to_units(h,s,l)
    return TupleMath.floor(TupleMath.scale(UNIT_TO_PYGAME, colorsys.hls_to_rgb(h,l,s)))

def str_to_color(v: str):
    v = v.strip()
    while not v[0].isalnum():
        v = v[1:]
    charcnt = len(v)
    if charcnt == 3:
        return (int(v[0], 16) * 17, int(v[1], 16) * 17, int(v[2], 16) * 17)
    elif charcnt == 4:
        return (int(v[0], 16) * 17, int(v[1], 16) * 17, int(v[2], 16) * 17, int(v[3], 16) * 17)
    elif charcnt == 6:
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
    elif charcnt == 8:
        return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16), int(v[6:8], 16))
    else:
        raise ValueError(f"Invalid number of characters in a parsed color, expected 3, 4, 6 or 8 characters, received {charcnt}, stripped string: {v}")

class Gradient():
    def __init__(self, kvps: list[tuple[float,tuple[int,int,int]]]):
        self.kvps = sorted(kvps)
    def eval(self, t) -> tuple[int]:
        left_k, left_v = self.kvps[0]
        for k,v in self.kvps:
            if t < k:
                return lerp(left_v, v, (t - left_k)/(k - left_k))
            left_k, left_v = k,v
        return left_v

def parse_gradient(raw_gradient: dict[str,str]) -> Gradient:
    return Gradient((float(k), str_to_color(v)) for k,v in raw_gradient.items())

class TupleMath:
    T = TypeVar("T")
    @staticmethod
    def diff_internal(tuple: tuple[T], return_abs: bool = False) -> T:
        assert len(tuple) == 2
        raw = tuple[1] - tuple[0]
        return abs(raw) if return_abs else raw
    @staticmethod
    def sub(a: tuple[T], b: tuple[T], return_abs: bool = False) -> tuple[T]:
        return tuple(abs(x - y) if return_abs else x - y for x, y in zip(a,b))
    @staticmethod
    def add(*tuples: tuple[T]) -> tuple[T]:
        return tuple(sum(x) for *x, in zip(*tuples))
    @staticmethod
    def mult(*tuples: tuple[T]) -> tuple[T]:
        return tuple(prod(x) for *x, in zip(*tuples))
    @staticmethod
    def scale(scalar: T, values: tuple[T]) -> tuple[T]:
        return tuple(scalar * v for v in values)
    @staticmethod
    def neg(values: tuple[T]) -> tuple[T]:
        return tuple(-v for v in values)
    @staticmethod
    def floor(values: tuple[T]) -> tuple[int]:
        return tuple(math.floor(v) for v in values)
    def ceil(values: tuple[T]) -> tuple[int]:
        return tuple(math.ceil(v) for v in values)
    def round(values: tuple[T]) -> tuple[int]:
        return tuple(math.floor(v+0.5) for v in values)
