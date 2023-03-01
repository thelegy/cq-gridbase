from . import Spec, getSpec
from .common import magnetHole, outline, smoothHole

from cqwild import Face, PrintSettings, WP
from functools import cache
from math import cos, pi
from typing import Optional

import apply_to_each_face as eachFace
import cqwild as cq


@cache
def recepticle(
        square: bool = False,
        spec: Optional[Spec] = None,
        ) -> WP:
    spec = getSpec() if spec is None else spec
    w = (
        WP("XY")
        .placeSketch(outline(square=square, spec=spec))
        .extrude(spec.profile_height())
        .faces(">Z")
        .placeSketch(outline(spec=spec))
    )
    first = True
    for height, taper in spec.profile:
        if not first:
            w = w.faces("|Z").wires(">>Z[1]").toPending()
        w = w.cutBlind(-height/cos(taper/180*pi), taper=taper)
        first = False
    return w


@cache
def tile(
        extra_height: Optional[float] = None,
        cornerHoleBoreDiameter: float = 0,
        cornerHoleHeadDiameter: float = 0,
        cornerHoleAngle: float = 90,
        spec: Optional[Spec] = None,
        pSettings: PrintSettings = PrintSettings(),
        ) -> WP:
    spec = getSpec() if spec is None else spec
    extra_height = spec.sizeZ if extra_height is None else extra_height
    magnetInset = spec.clearance + spec.profile_width() + spec.magnetInset
    topCut = spec.topCut(pSettings.nozzleDiameter)
    fillet = 1.5
    w = (
        recepticle(square=True, spec=spec)
        .faces("<Z")
        .tag("base_top")
        .placeSketch(
            outline(square=True, spec=spec)
            .rect(spec.sizeXY-2*magnetInset-spec.magnetDiameter-2*spec.magnetThicken, spec.sizeXY-2*spec.profile_width(), mode="s")
            .rect(spec.sizeXY-2*spec.profile_width(), spec.sizeXY-2*magnetInset-spec.magnetDiameter-2*spec.magnetThicken, mode="s")
            .vertices("(<<X[2] or >>X[2]) and (<<Y[2] or >>Y[2])")
            .fillet(spec.magnetDiameter-2*spec.magnetThicken)
            .edges()
            .vertices("<<X[1] or >>X[1] or <<Y[1] or >>Y[1]")
            .fillet(2)
        )
        .extrude(-extra_height)

        .workplaneFromTagged("base_top")
        .rect(spec.sizeXY-2*magnetInset, spec.sizeXY-2*magnetInset, forConstruction=True)
        .apply(magnetHole, spec.magnetDiameter, spec.magnedDepth, spec.magnetDiameterSub, pSettings=pSettings)

        .workplaneFromTagged("base_top")
        .workplane(offset=spec.profile_height()-topCut)
        .placeSketch(outline(square=True, spec=spec))
        .cutBlind(topCut)
    )
    if cornerHoleHeadDiameter > 0 and cornerHoleBoreDiameter > 0:
        w = (
            w

            .faces(">Z")
            .vertices("(<X or >X) and (<Y or >Y)")
            .apply(smoothHole, cornerHoleHeadDiameter, fillet)

            .edges("|Z and (<X or >X) and (<Y or >Y)")
            .vertices(">Z")
            .hole(cornerHoleHeadDiameter, (spec.profile_height()-topCut-fillet))

            .edges("|Z and (<X or >X) and (<Y or >Y)")
            .vertices(">Z")
            .cskHole(cornerHoleBoreDiameter, cornerHoleHeadDiameter, cornerHoleAngle)
        )
    return w


@cache
def baseplate(
        x_size: int = 1,
        y_size: int = 1,
        extra_height: Optional[float] = None,
        cornerHoleBoreDiameter: float = 0,
        cornerHoleHeadDiameter: float = 0,
        cornerHoleAngle: float = 90,
        spec: Optional[Spec] = None,
        pSettings: PrintSettings = PrintSettings(),
    ) -> WP:
    spec = getSpec() if spec is None else spec
    def screwHoles(rawW: cq.cq.Workplane, _: Face) -> WP:
        w = (
            WP._fromCQ(rawW)
            .center(0, -spec.profile_height()/2)

            .pushPoints([(-5.5, 0), (0, 0), (5.5, 0)])
            .circle(3.5/2)
            .extrude(-spec.profile_width())

            .workplane(offset=-spec.profile_width()/2)
            .slot2D(17, 6)
            .extrude(spec.profile_width()-min(spec.sizeXY, spec.sizeXY)/2)
        )
        return w
    w = (
        WP("XY")
        .rarray(spec.sizeXY, spec.sizeXY, x_size, y_size)
        .eachpoint(tile(
                extra_height=extra_height,
                cornerHoleBoreDiameter=cornerHoleBoreDiameter,
                cornerHoleHeadDiameter=cornerHoleHeadDiameter,
                cornerHoleAngle=cornerHoleAngle,
                spec=spec,
                pSettings=pSettings,
            ).findSolid().moved,
            combine=True)

        .faces("<Z")
        .chamfer(.5)

        .faces("<X or >X or <Y or >Y")
        .applyCQ(
            eachFace.applyToEachFace,
            eachFace.XAxisInPlane(eachFace.WORLD_AXIS_PLANES_XY_ZX_YZ),
            screwHoles,
            combine="cut",
        )
    )
    return w
