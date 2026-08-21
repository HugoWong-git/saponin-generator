"""2-D map folding: an m x n grid of unit cells under all-layers simple folds.

WHY THIS DOMAIN, AND WHAT IT ADDS OVER THE 1-D STRIP
----------------------------------------------------
`smoke_test/strip.py` validated the search machinery on a 1 x n strip. That domain's
layer order is a *total* order forced by the fold history, which is exactly why its
legality check is cheap and exact -- and exactly why the result said nothing about the
parent project's real blocker.

The obvious next rung is a single interior vertex. It is the wrong rung. All sectors
around one vertex meet *at* the vertex, so they all overlap and the stacking is still a
total order; worse, single-vertex flat-foldability is completely characterised by local
conditions (Kawasaki + Maekawa + big-little-big), so a valid M/V assignment *guarantees*
a consistent layer ordering exists. Layer order never independently obstructs there.

A grid does obstruct, for a reason that is easy to state and is the whole point of this
module: **two crease directions share one layer order**. Geometry stays 1-D in each axis
(x depends only on the column, y only on the row, because an all-layers fold moves whole
columns or whole rows). What couples them is the stack. A vertical fold's legality
depends on ranks that horizontal folds produced, and vice versa. That coupling is the
2-D content, isolated from everything else.

THE LABEL-CONSISTENCY CONDITION (the interesting constraint)
------------------------------------------------------------
Assignments live on crease *segments*, not crease lines -- ``vmv[r][c]`` is the unit
edge between cells (r,c) and (r,c+1). This is forced, not a modelling choice: a grid's
interior vertex has four incident creases at 90 degrees, so Kawasaki is automatic, but
Maekawa needs |M - V| = 2. If a crease line carried one uniform label, each vertex would
see two copies of two labels, giving |M - V| in {0, 4}, and *no* grid would ever be
flat-foldable. Real maps fold, so labels must vary along a line.

An all-layers simple fold rotates one side, all layers together, as a single rigid block.
So there is exactly one global over/under bit for the whole fold, and each row's segment
realises a label determined by that bit and by that row's face orientation:

    realised(r) is VALLEY  iff  over == (face(r) > 0),        face(r) = oys[r] * oxs[c]

The fold is only available when every row's required label agrees on the same ``over``.
Since ``oys[r]`` starts uniform and flips as horizontal folds happen, *which vertical
folds are available changes as horizontal folds are made*. Order matters, in a way it
never did in 1-D. Worked example, the 2x2 map: fold vertically (both segments of the
vertical crease must match), which flips ``oxs`` for one column; the horizontal crease
then requires opposite labels in its two columns -- V on one side, M on the other. That
is precisely the 3-1 split Maekawa demands at the single interior vertex.

EQUIVALENCE TO THE 1-D CASE
---------------------------
With m = 1 there are no horizontal creases and no row orientation to vary, so this
reduces exactly to `smoke_test/strip.py`. `tests/test_grid.py` checks that against the
strip implementation over every reachable state, which is the strongest correctness
evidence available for the 2-D code: a real second implementation, not a restatement.

Coordinates: cell (r, c) starts at x = c, y = r, both orientations +1. ``oxs[c]`` is +1
when column c is face-up in x and doubles as its forward direction, matching the strip
convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

MOUNTAIN = "M"
VALLEY = "V"

SIDE_LOW = 0   # columns 0..c (or rows 0..r) move
SIDE_HIGH = 1  # columns c+1.. (or rows r+1..) move

AXIS_V = 0  # fold about a vertical crease line: columns move, x reflects
AXIS_H = 1  # fold about a horizontal crease line: rows move, y reflects


@dataclass(frozen=True)
class GridState:
    """Immutable folded state of the map.

    m, n:        rows and columns of unit cells
    hmv:         (m-1) x n required labels; hmv[r][c] is the edge between (r,c),(r+1,c)
    vmv:         m x (n-1) required labels; vmv[r][c] is the edge between (r,c),(r,c+1)
    xpos, oxs:   per-column cell coordinate and orientation (the x-axis strip)
    ypos, oys:   per-row cell coordinate and orientation (the y-axis strip)
    panel_rank:  bottom-to-top rank of each panel, flattened as pr * (nV + 1) + pc
    hfolded:     bitmask over the m-1 horizontal crease lines
    vfolded:     bitmask over the n-1 vertical crease lines
    step:        number of folds applied
    """

    m: int
    n: int
    hmv: tuple[tuple[str, ...], ...]
    vmv: tuple[tuple[str, ...], ...]
    xpos: tuple[int, ...]
    oxs: tuple[int, ...]
    ypos: tuple[int, ...]
    oys: tuple[int, ...]
    panel_rank: tuple[int, ...]
    hfolded: int
    vfolded: int
    step: int

    # -- derived -------------------------------------------------------------------

    @property
    def n_v_folded(self) -> int:
        return bin(self.vfolded).count("1")

    @property
    def n_h_folded(self) -> int:
        return bin(self.hfolded).count("1")

    def panel_col(self, c: int) -> int:
        return bin(self.vfolded & ((1 << c) - 1)).count("1")

    def panel_row(self, r: int) -> int:
        return bin(self.hfolded & ((1 << r) - 1)).count("1")

    def rank(self, r: int, c: int) -> int:
        return self.panel_rank[
            self.panel_row(r) * (self.n_v_folded + 1) + self.panel_col(c)
        ]

    def face(self, r: int, c: int) -> int:
        """+1 if cell (r,c) is face-up. Two mirror flips compose to a rotation."""
        return self.oys[r] * self.oxs[c]

    def v_boundary(self, c: int) -> int:
        """x-coordinate of vertical crease line c: the forward edge of column c."""
        return self.xpos[c] + (1 if self.oxs[c] > 0 else 0)

    def h_boundary(self, r: int) -> int:
        return self.ypos[r] + (1 if self.oys[r] > 0 else 0)

    def is_folded(self, axis: int, k: int) -> bool:
        mask = self.vfolded if axis == AXIS_V else self.hfolded
        return bool(mask >> k & 1)

    @property
    def n_folded(self) -> int:
        return self.n_h_folded + self.n_v_folded

    @property
    def is_solved(self) -> bool:
        return self.n_h_folded == self.m - 1 and self.n_v_folded == self.n - 1


def initial_state(
    hmv: tuple[tuple[str, ...], ...], vmv: tuple[tuple[str, ...], ...]
) -> GridState:
    m = len(vmv)
    n = len(hmv[0]) if hmv else (len(vmv[0]) + 1 if vmv and vmv[0] else 1)
    return GridState(
        m=m,
        n=n,
        hmv=tuple(tuple(row) for row in hmv),
        vmv=tuple(tuple(row) for row in vmv),
        xpos=tuple(range(n)),
        oxs=(1,) * n,
        ypos=tuple(range(m)),
        oys=(1,) * m,
        panel_rank=(0,),
        hfolded=0,
        vfolded=0,
        step=0,
    )


# -----------------------------------------------------------------------------------
# Legality: the exact layer-crossing check, now over one stack shared by both axes
# -----------------------------------------------------------------------------------

def _crosses(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """True if two rank intervals interleave (neither nested nor disjoint)."""
    a0, a1 = sorted(a)
    b0, b1 = sorted(b)
    return a0 < b0 < a1 < b1 or b0 < a0 < b1 < a1


def check_no_crossing(state: GridState) -> tuple[bool, list[str]]:
    """Exact non-crossing test for the whole folded state.

    Same two failure modes as the 1-D case -- interleaved hairpins, and a hairpin
    enclosing a cell that occupies the square it bulges into -- but arcs from *both*
    crease directions are now indexed by their full folded location, and every rank
    comes from one shared stack. Two hairpins only conflict when they sit at the same
    line, bulge the same way, and lie in the same row/column of the folded plane; that
    is where a vertical fold can be blocked by ranks a horizontal fold created.

    A cell that merely *ends* at the crease is not enclosed by a hairpin bulging past it
    -- it stops before the turn -- so only the far-side cells are tested.
    """
    violations: list[str] = []

    # location -> list of rank intervals. Location carries the axis, the line
    # coordinate, the bulge direction, and the position along the line.
    arcs: dict[tuple, list[tuple[int, int]]] = {}
    # the square each group of arcs bulges into
    target: dict[tuple, tuple[int, int]] = {}

    for c in range(state.n - 1):
        if not state.is_folded(AXIS_V, c):
            continue
        x = state.v_boundary(c)
        into_x = x if state.oxs[c] > 0 else x - 1
        for r in range(state.m):
            key = (AXIS_V, x, state.oxs[c] > 0, state.ypos[r])
            arcs.setdefault(key, []).append((state.rank(r, c), state.rank(r, c + 1)))
            target[key] = (into_x, state.ypos[r])

    for r in range(state.m - 1):
        if not state.is_folded(AXIS_H, r):
            continue
        y = state.h_boundary(r)
        into_y = y if state.oys[r] > 0 else y - 1
        for c in range(state.n):
            key = (AXIS_H, y, state.oys[r] > 0, state.xpos[c])
            arcs.setdefault(key, []).append((state.rank(r, c), state.rank(r + 1, c)))
            target[key] = (state.xpos[c], into_y)

    bodies: dict[tuple[int, int], set[int]] = {}
    for r in range(state.m):
        for c in range(state.n):
            bodies.setdefault((state.xpos[c], state.ypos[r]), set()).add(
                state.rank(r, c)
            )

    for key, group in arcs.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if _crosses(group[i], group[j]):
                    violations.append(
                        f"{key}: arcs {group[i]} and {group[j]} interleave"
                    )
        far = bodies.get(target[key], ())
        for a0, a1 in group:
            lo, hi = sorted((a0, a1))
            for rank in far:
                if lo < rank < hi:
                    violations.append(
                        f"{key}: arc ({lo},{hi}) encloses cell rank {rank}"
                    )
    return (not violations, violations)


# -----------------------------------------------------------------------------------
# Transition
# -----------------------------------------------------------------------------------

def fold_goes_over(label: str, face_before: int) -> bool:
    """Does the moving flap land on top? Same rule as the strip, with face = ox * oy."""
    return (label == VALLEY) == (face_before > 0)


def required_over(state: GridState, axis: int, k: int, side: int) -> bool | None:
    """The single over/under bit this fold must use, or None if no bit satisfies it.

    An all-layers fold is one rigid rotation, so every segment of the crease line has to
    realise its required label under the *same* bit. Disagreement means the fold is
    simply not available in this state -- which is how fold order comes to matter.
    """
    if axis == AXIS_V:
        moving_col = k if side == SIDE_LOW else k + 1
        wanted = {
            fold_goes_over(state.vmv[r][k], state.face(r, moving_col))
            for r in range(state.m)
        }
    else:
        moving_row = k if side == SIDE_LOW else k + 1
        wanted = {
            fold_goes_over(state.hmv[k][c], state.face(moving_row, c))
            for c in range(state.n)
        }
    return wanted.pop() if len(wanted) == 1 else None


def _rebuild_ranks(
    state: GridState, axis: int, k: int, moving: set[int], over: bool
) -> tuple[int, ...]:
    """Total order after the fold.

    Stationary panels keep their relative order; moving panels keep theirs but reversed
    (a flipped stack is upside down); the moving block goes entirely above or below.
    """
    new_v = state.vfolded | ((1 << k) if axis == AXIS_V else 0)
    new_h = state.hfolded | ((1 << k) if axis == AXIS_H else 0)
    n_v, n_h = bin(new_v).count("1"), bin(new_h).count("1")

    def new_pc(c: int) -> int:
        return bin(new_v & ((1 << c) - 1)).count("1")

    def new_pr(r: int) -> int:
        return bin(new_h & ((1 << r) - 1)).count("1")

    old_rank: list[int] = []
    is_moving: list[bool] = []
    for pr in range(n_h + 1):
        for pc in range(n_v + 1):
            r = next(r for r in range(state.m) if new_pr(r) == pr)
            c = next(c for c in range(state.n) if new_pc(c) == pc)
            old_rank.append(state.rank(r, c))
            is_moving.append((c if axis == AXIS_V else r) in moving)

    n_panels = len(old_rank)
    stationary = sorted(
        (p for p in range(n_panels) if not is_moving[p]), key=lambda p: old_rank[p]
    )
    movers = sorted(
        (p for p in range(n_panels) if is_moving[p]),
        key=lambda p: old_rank[p],
        reverse=True,
    )
    order = stationary + movers if over else movers + stationary

    ranks = [0] * n_panels
    for new_rank, p in enumerate(order):
        ranks[p] = new_rank
    return tuple(ranks)


def fold_unchecked(
    state: GridState, axis: int, k: int, side: int
) -> GridState | None:
    """Geometry of the fold with the crossing check omitted.

    Exposed so tests can ask both checkers about configurations ``apply_fold`` rejects;
    a rejected candidate still has to be a well-formed state to be judged. Returns None
    when the fold has no geometry at all: the crease is already folded, or the required
    labels disagree on the over/under bit.
    """
    limit = (state.n - 1) if axis == AXIS_V else (state.m - 1)
    if not 0 <= k < limit or side not in (SIDE_LOW, SIDE_HIGH):
        raise ValueError(f"bad action (axis={axis}, k={k}, side={side})")
    if state.is_folded(axis, k):
        return None

    over = required_over(state, axis, k, side)
    if over is None:
        return None
    return fold_with_over(state, axis, k, side, over)


def fold_with_over(
    state: GridState, axis: int, k: int, side: int, over: bool
) -> GridState:
    """The fold geometry given the over/under bit outright, skipping label lookup.

    Instance generation needs this: it *derives* the labels from a fold sequence rather
    than being handed them, so it chooses ``over`` first and reads off what each segment
    must be. Callers that have labels should use ``fold_unchecked``, which computes the
    bit and then calls this.
    """
    limit = (state.n - 1) if axis == AXIS_V else (state.m - 1)
    moving = set(range(0, k + 1) if side == SIDE_LOW else range(k + 1, limit + 1))

    xpos, oxs = list(state.xpos), list(state.oxs)
    ypos, oys = list(state.ypos), list(state.oys)
    if axis == AXIS_V:
        x0 = state.v_boundary(k)
        for c in moving:
            xpos[c] = 2 * x0 - xpos[c] - 1
            oxs[c] = -oxs[c]
    else:
        y0 = state.h_boundary(k)
        for r in moving:
            ypos[r] = 2 * y0 - ypos[r] - 1
            oys[r] = -oys[r]

    # Normalise each axis to start at 0. The fold is translation-invariant, so this
    # only affects the transposition key -- without it, states identical up to a shift
    # hash apart and the search re-explores them.
    dx, dy = min(xpos), min(ypos)

    return GridState(
        m=state.m,
        n=state.n,
        hmv=state.hmv,
        vmv=state.vmv,
        xpos=tuple(x - dx for x in xpos),
        oxs=tuple(oxs),
        ypos=tuple(y - dy for y in ypos),
        oys=tuple(oys),
        panel_rank=_rebuild_ranks(state, axis, k, moving, over),
        hfolded=state.hfolded | ((1 << k) if axis == AXIS_H else 0),
        vfolded=state.vfolded | ((1 << k) if axis == AXIS_V else 0),
        step=state.step + 1,
    )


@lru_cache(maxsize=1 << 18)
def apply_fold(state: GridState, axis: int, k: int, side: int) -> GridState | None:
    """Pure transition. Returns a new state, or None if the fold is illegal.

    Illegal means: already folded, the required labels disagree on over/under, or the
    result would push paper through paper.

    Memoised because the search asks the same question twice: ``legal_actions`` builds
    every candidate and its crossing check to decide legality, then the tree discards
    all but one and asks for it again. States are frozen and hashable, and the function
    is pure, so caching is safe and roughly halves the transition cost.
    """
    candidate = fold_unchecked(state, axis, k, side)
    if candidate is None:
        return None
    return candidate if check_no_crossing(candidate)[0] else None


# -----------------------------------------------------------------------------------
# Action codec
# -----------------------------------------------------------------------------------

def action_size(m: int, n: int) -> int:
    return 2 * ((n - 1) + (m - 1))


def encode(m: int, n: int, axis: int, k: int, side: int) -> int:
    base = 0 if axis == AXIS_V else 2 * (n - 1)
    return base + 2 * k + side


def decode(m: int, n: int, action: int) -> tuple[int, int, int]:
    v_actions = 2 * (n - 1)
    if action < v_actions:
        return AXIS_V, action // 2, action % 2
    action -= v_actions
    return AXIS_H, action // 2, action % 2


def legal_actions(state: GridState) -> list[int]:
    out = []
    for a in range(action_size(state.m, state.n)):
        axis, k, side = decode(state.m, state.n, a)
        if apply_fold(state, axis, k, side) is not None:
            out.append(a)
    return out


# -----------------------------------------------------------------------------------
# Game interface (single-player, alpha-zero-general shape)
# -----------------------------------------------------------------------------------

class GridGame:
    """Single-player Game over one map-folding instance.

    Same contract as ``smoke_test.strip.StripGame``: player is pinned to 1,
    ``getCanonicalForm`` is the identity, and ``getGameEnded`` returns 0.0 for
    "not terminal" with genuine terminal scores clamped away from zero.
    """

    def __init__(
        self, hmv: tuple[tuple[str, ...], ...], vmv: tuple[tuple[str, ...], ...]
    ):
        self.hmv = tuple(tuple(row) for row in hmv)
        self.vmv = tuple(tuple(row) for row in vmv)
        self.m = len(self.vmv)
        self.n = len(self.hmv[0]) if self.hmv else len(self.vmv[0]) + 1

    def getInitBoard(self) -> GridState:
        return initial_state(self.hmv, self.vmv)

    def getBoardSize(self) -> tuple[int, int]:
        return (self.m, self.n)

    def getActionSize(self) -> int:
        return action_size(self.m, self.n)

    def getNextState(self, state: GridState, player: int, action: int):
        axis, k, side = decode(self.m, self.n, action)
        nxt = apply_fold(state, axis, k, side)
        if nxt is None:
            raise ValueError(f"illegal action {action}")
        return nxt, 1

    def getValidMoves(self, state: GridState, player: int = 1) -> list[int]:
        legal = set(legal_actions(state))
        return [1 if a in legal else 0 for a in range(self.getActionSize())]

    def getGameEnded(self, state: GridState, player: int = 1) -> float:
        if state.is_solved:
            return 1.0
        if not legal_actions(state):
            # Clamped away from 0.0, which is the "not terminal" sentinel.
            total = (self.m - 1) + (self.n - 1)
            return -1.0 + 0.5 * state.n_folded / max(total, 1)
        return 0.0

    def getCanonicalForm(self, state: GridState, player: int = 1) -> GridState:
        return state

    def getSymmetries(self, state: GridState, pi):
        return [(state, pi)]

    def stringRepresentation(self, state: GridState) -> str:
        # Must include the stack: same folded silhouette with different stacking is a
        # genuinely different state, and merging them would corrupt the search.
        return (
            f"{state.xpos}{state.oxs}{state.ypos}{state.oys}"
            f"{state.panel_rank}{state.hfolded},{state.vfolded}"
        )
