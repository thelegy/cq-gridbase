from cqwild import Location, PrintSettings, Shape, Sketch, WP
from functools import cache
from math import pi
from src.cqgridbase import Spec, getSpec
from typing import Optional

import cqwild as cq


@cache
def outline(
        square: bool = False,
        inner: bool = False,
        spec: Optional[Spec] = None,
        ) -> Sketch:
    spec = getSpec() if spec is None else spec
    offset = spec.clearance if inner else 0
    s = Sketch().rect(spec.sizeXY-2*offset, spec.sizeXY-2*offset)
    if not square:
        s = s.vertices().fillet(spec.fillet/2-offset)
    return s


def magnetHole(
        w: WP,
        diameter: float,
        thickness: float,
        diameterSub: float,
        depthSub: Optional[float] = None,
        pSettings: PrintSettings = PrintSettings(),
        ) -> WP:
    def guard(p: Location) -> Shape:
        (x, y, _), _ = p.toTuple()
        r = cq.Vector(x, y).getSignedAngle(cq.Vector(0, 1))/pi*180
        return (
            WP("XY")
            .rect(diameter+.1, 2.5*pSettings.nozzleDiameter)
            .extrude(-1.5*pSettings.layerHeight)
            .rotateAboutCenter((0, 0, 1), r)
            .findSolid()
            .moved(p)
        )
    diamClearance = diameter + .75*pSettings.nozzleDiameter
    diamLock = diameter + .1*pSettings.nozzleDiameter
    depthClearance = thickness + 3*pSettings.layerHeight
    w = (
        w
        .tag("magnets")

        .apply(cq.print.steppedHoleDownwards, diamClearance, depthClearance, diameterSub, depthSub)

        .vertices(tag="magnets")
        .circle(diamClearance/2)
        .circle(diamLock/2)
        .extrude(-2.5*pSettings.layerHeight)

        .vertices(tag="magnets")
        .eachpoint(guard, combine=True)
    )
    return w


def smoothHole(
        w: WP,
        diameter: float,
        depth: float,
        ) -> WP:
    @cache
    def smoothHoleNegative(diameter: float, depth : float) -> Shape:
        return (
            WP("XZ")
            .spline([
                    (diameter/2, -depth),
                    (diameter/2+depth, 0),
                ], [
                    (0, 1),
                    (1, 0),
                ])
            .lineTo(0, 0)
            .lineTo(0, -depth)
            .close()
            .revolve(axisStart=(0, 0, 0), axisEnd=(0, 1, 0))
            .findSolid()
        )
    return w.cutEach(smoothHoleNegative(diameter, depth).moved)
