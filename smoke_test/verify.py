"""Independent geometric verifier for a folded strip state.

``strip.check_no_crossing`` decides legality combinatorially (rank intervals at each
boundary).  This module decides the same question a completely different way: it renders
the folded paper as an explicit polyline in the (x, z) plane and runs all-pairs
segment-segment intersection.  Pass criterion P1 compares the two over every state the
brute-force search reaches, so a shared bug would have to occur twice, in two different
formalisms, to go unnoticed.

Rendering
---------
Segment s is the horizontal chord from (pos[s], z_s) to (pos[s]+1, z_s), with z_s its
panel rank.  A folded crease is a hairpin bulging a distance delta into the neighbouring
cell: two horizontal stubs plus one vertical riser.  Delta grows with the hairpin's rank
span, so a properly nested hairpin sits inside its parent and touches nothing, while two
interleaving hairpins are forced onto the same riser line and register as a collinear
overlap.
"""

from __future__ import annotations

from .strip import StripState

Point = tuple[float, float]
Seg = tuple[Point, Point]


def _orient(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on(a: Point, b: Point, p: Point) -> bool:
    return (
        min(a[0], b[0]) - 1e-12 <= p[0] <= max(a[0], b[0]) + 1e-12
        and min(a[1], b[1]) - 1e-12 <= p[1] <= max(a[1], b[1]) + 1e-12
    )


def segments_cross(s1: Seg, s2: Seg) -> bool:
    """True if two closed segments share a point, ignoring shared endpoints.

    Collinear overlap of more than a point counts as a crossing -- that is how two
    interleaving hairpins on the same riser line are caught.
    """
    (a, b), (c, d) = s1, s2
    shared = {a, b} & {c, d}
    d1, d2 = _orient(c, d, a), _orient(c, d, b)
    d3, d4 = _orient(a, b, c), _orient(a, b, d)

    if abs(d1) < 1e-12 and abs(d2) < 1e-12:
        # collinear: overlapping in more than the shared endpoint?
        pts = [p for p in (a, b) if _on(c, d, p)] + [p for p in (c, d) if _on(a, b, p)]
        return len({p for p in pts} - shared) > 0
    if shared:
        return False
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return True
    for p, (q, r) in ((a, (c, d)), (b, (c, d)), (c, (a, b)), (d, (a, b))):
        if abs(_orient(q, r, p)) < 1e-12 and _on(q, r, p):
            return True
    return False


def polyline(state: StripState) -> list[Seg]:
    """Explicit (x, z) rendering of the folded paper."""
    segs: list[Seg] = []
    z = [float(state.rank_of(s)) for s in range(state.n)]
    for s in range(state.n):
        segs.append(((float(state.pos[s]), z[s]), (float(state.pos[s] + 1), z[s])))

    for c in range(state.n - 1):
        if not state.is_folded(c):
            continue
        x = float(state.crease_boundary(c))
        span = abs(z[c] - z[c + 1])
        delta = (0.05 + 0.4 * span / (state.n + 1)) * (1 if state.orient[c] > 0 else -1)
        tip = x + delta
        segs.append(((x, z[c]), (tip, z[c])))
        segs.append(((tip, z[c]), (tip, z[c + 1])))
        segs.append(((tip, z[c + 1]), (x, z[c + 1])))
    return segs


def geometric_no_crossing(state: StripState) -> bool:
    segs = polyline(state)
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if segments_cross(segs[i], segs[j]):
                return False
    return True
