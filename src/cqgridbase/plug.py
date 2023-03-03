from . import Spec, getSpec
from .common import magnetSocket, outline

from cqwild import Location, PrintSettings, Shape, WP
from functools import cache
from math import ceil, cos, pi
from typing import Optional

import cqwild as cq


@cache
def plug(
        spec: Optional[Spec] = None,
        pSettings: PrintSettings = PrintSettings(),
        ) -> Shape:
    spec = getSpec() if spec is None else spec
    magnetInset = spec.clearance + spec.profile_width() + spec.magnetInset
    w = (
        WP("XY")
        .placeSketch(outline(inner=True, spec=spec))
    )
    first = True
    for height, taper in spec.profile:
        if not first:
            w = w.wires("<Z").toPending()
        w = w.extrude(-height/cos(taper/180*pi), taper=taper)
        first = False
    def magnets(p: Location) -> Shape:
        (x, y, _), _ = p.toTuple()
        rotation = cq.Vector(x, y).getSignedAngle(cq.Vector(0, 1))/pi*180
        return magnetSocket(spec.magnetDiameter, spec.magnedDepth, rotation=rotation, bottomGrid=2*pSettings.layerHeight, anchor="bottom", pSettings=pSettings).moved(p)
    w = (
        w
        .faces("<Z")
        # .workplane(offset=2*pSettings.layerHeight, invert=True)
        .rect(spec.sizeXY-2*magnetInset, spec.sizeXY-2*magnetInset, forConstruction=True)
        .vertices()
        .eachpoint(magnets, combine="cut")
    )
    return w.findSolid()


@cache
def plugBase(
        height: float = 0,
        x_size: int = 1,
        y_size: int = 1,
        square: bool = False,
        spec: Optional[Spec] = None,
        pSettings: PrintSettings = PrintSettings(),
        ) -> WP:
    spec = getSpec() if spec is None else spec
    height = ceil(spec.profile_height() / spec.sizeZ) if height <= 0 else height
    pad = height * spec.sizeZ - spec.profile_height()
    w = (
        WP("XY")
        .rect(x_size*spec.sizeXY-2*spec.clearance, y_size*spec.sizeXY-2*spec.clearance)
        .extrude(max(pad, 0.001))
    )
    if not square:
        w = w.edges("|Z").fillet(spec.fillet/2-spec.clearance)
    w = (
        w
        .rarray(spec.sizeXY, spec.sizeXY, x_size, y_size)
        .eachpoint(plug(spec=spec, pSettings=pSettings).moved, combine=True)
    )
    return w
