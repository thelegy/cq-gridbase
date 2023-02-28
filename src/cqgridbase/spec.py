from functools import cache
from math import pi, tan
from typing import NamedTuple, Optional


class Spec(NamedTuple):
    profile: tuple[tuple[float, float], ...]
    sizeXY: float
    fillet: float

    magnetInset: float
    magnetDiameter: float = 6
    magnetDiameterSub: float = 3.75
    magnedDepth: float = 2
    magnetThicken: float = 1.2

    clearance: float = 0.25
    sizeZ: float = 1

    @cache
    def profile_width(self: 'Spec') -> float:
        acc = 0
        for height, taper in self.profile:
            acc += height*tan(taper/180*pi)
        return acc

    @cache
    def profile_height(self: 'Spec') -> float:
        acc = 0
        for height, _ in self.profile:
            acc += height
        return acc


SPEC: Optional[Spec] = None


def getSpec() -> Spec:
    global SPEC
    if SPEC is None:
        raise Exception("No global SPEC is set")
    return SPEC


def setSpec(spec: Spec):
    global SPEC
    SPEC = spec
