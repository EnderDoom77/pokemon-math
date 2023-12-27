from typing import Generic, TypeVar


def lerp(left: tuple | list, right: tuple | list, t: float) -> tuple:
    return tuple([l + (r-l)*t for l,r in zip(left, right)])

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