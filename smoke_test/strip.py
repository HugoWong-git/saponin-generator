"""1-D strip folding environment -- the reduced domain for the M1.5 smoke test.

WHY 1-D
-------
A 1xn strip divided into n unit segments by n-1 creases, each labelled mountain or
valley ("simple folds / map folding in 1-D", cf. Arkin et al., *When Can You Fold a
Map?*).  Geometry is trivial (segments on a line, every fold +/-180 degrees) but the
layer-ordering constraint -- the thing Kawasaki and Maekawa cannot see and the crux of
the parent project -- survives intact and is exactly checkable.

GEOMETRY MODEL
--------------
The paper is a polyline in the (x, z) plane.  Segment s occupies the closed unit cell
``[pos[s], pos[s]+1]``.  Folds are 180-degree rotations about a crease point, which in
the (x, z) plane map ``(x, z) -> (2*x0 - x, 2*h - z)``: the x-coordinate reflects AND
the layer order of the moving block reverses AND every moving segment turns over.

PANELS AND THE LAYER ORDER
--------------------------
A *panel* is a maximal run of consecutive segments whose connecting creases are all
still unfolded.  A panel is straight, so all its segments lie at the same physical
height.  ``panel_rank`` is a total order (bottom to top) over panels.

The total order is not an arbitrary linearisation: a simple fold physically lifts the
whole moving flap over (or under) the *entire* stationary stack, so the fold history
determines the order completely.  Nothing is chosen arbitrarily, and nothing is
over-constrained.

ORIENTATION == DIRECTION
------------------------
``orient[s]`` is +1 when segment s still has its original top face up.  Because a fold
reflects x and z together, the segment's forward direction along the paper flips at
exactly the same moments its face does.  Both start at +1, so they are the same number:
``orient[s]`` also says whether walking from segment s to segment s+1 moves rightwards.
This is used to place creases on the correct side of a cell.

WHY THE ACTION IS ONLY (crease, side)
-------------------------------------
A flap can fold over the top or under the bottom, which are different states.  But the
crease already carries a required M/V label, and:

  * OVER  -> the moving segment ends up above, face flipped, so the crease is a valley
             exactly when the pair was face-up before the fold;
  * UNDER -> the stationary segment ends up above unflipped, so the crease is a valley
             exactly when the pair was face-down before the fold.

The two adjacent segments share a panel before the fold, hence share an orientation, so
the label plus that orientation pins over/under uniquely.  The free choice collapses and
the action space is exactly ``2 * (n-1)`` -- (which crease, which side moves) -- as the
task specifies.
"""

from __future__ import annotations

from dataclasses import dataclass

MOUNTAIN = "M"
VALLEY = "V"

SIDE_LEFT = 0   # segments 0..crease move
SIDE_RIGHT = 1  # segments crease+1..n-1 move


@dataclass(frozen=True)
class StripState:
    """Immutable folded state of the strip.

    n:          number of unit segments
    mv:         tuple of n-1 labels, mv[c] is the required assignment of crease c
    pos:        cell index of each segment
    orient:     +1 face-up / -1 face-down; doubles as forward direction (see module doc)
    panel_rank: bottom-to-top rank of each panel; panel index of segment s is the number
                of folded creases strictly before s
    folded:     bitmask of folded creases
    step:       number of folds applied
    """

    n: int
    mv: tuple[str, ...]
    pos: tuple[int, ...]
    orient: tuple[int, ...]
    panel_rank: tuple[int, ...]
    folded: int
    step: int

    # -- derived -------------------------------------------------------------------

    def panel_of(self, s: int) -> int:
        return bin(self.folded & ((1 << s) - 1)).count("1")

    def rank_of(self, s: int) -> int:
        return self.panel_rank[self.panel_of(s)]

    def crease_boundary(self, c: int) -> int:
        """x-coordinate of crease c: the forward edge of segment c."""
        return self.pos[c] + (1 if self.orient[c] > 0 else 0)

    def is_folded(self, c: int) -> bool:
        return bool(self.folded >> c & 1)

    @property
    def n_folded(self) -> int:
        return bin(self.folded).count("1")

    @property
    def is_solved(self) -> bool:
        return self.n_folded == self.n - 1


def initial_state(mv: tuple[str, ...]) -> StripState:
    n = len(mv) + 1
    return StripState(
        n=n,
        mv=tuple(mv),
        pos=tuple(range(n)),
        orient=(1,) * n,
        panel_rank=(0,),
        folded=0,
        step=0,
    )


# -----------------------------------------------------------------------------------
# Legality: the exact layer-crossing check
# -----------------------------------------------------------------------------------

def _crosses(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """True if two rank intervals interleave (neither nested nor disjoint)."""
    a0, a1 = sorted(a)
    b0, b1 = sorted(b)
    return a0 < b0 < a1 < b1 or b0 < a0 < b1 < a1


def check_no_crossing(state: StripState) -> tuple[bool, list[str]]:
    """Exact non-crossing test for the whole folded state.

    At every integer boundary x the paper presents:
      * R-arcs  -- folded creases whose hairpin bulges into x+eps,
      * L-arcs  -- folded creases whose hairpin bulges into x-eps,
      * bodies  -- segments occupying cell x (present at x+eps) or cell x-1 (at x-eps).

    Paper passes through paper exactly when
      1. two arcs on the same side interleave in rank, or
      2. an arc encloses the rank of a body occupying the cell the arc bulges into.

    A segment that merely *ends* at x is not enclosed by an arc bulging past x -- it
    stops before the hairpin -- which is why only the far-side bodies are tested.
    """
    violations: list[str] = []
    r_arcs: dict[int, list[tuple[int, int]]] = {}
    l_arcs: dict[int, list[tuple[int, int]]] = {}
    for c in range(state.n - 1):
        if not state.is_folded(c):
            continue
        x = state.crease_boundary(c)
        arc = (state.rank_of(c), state.rank_of(c + 1))
        (r_arcs if state.orient[c] > 0 else l_arcs).setdefault(x, []).append(arc)

    bodies: dict[int, set[int]] = {}
    for s in range(state.n):
        bodies.setdefault(state.pos[s], set()).add(state.rank_of(s))

    for side_name, arcs_at, body_cell in (
        ("R", r_arcs, lambda x: x),      # bulges into x+eps == cell x
        ("L", l_arcs, lambda x: x - 1),  # bulges into x-eps == cell x-1
    ):
        for x, arcs in arcs_at.items():
            for i in range(len(arcs)):
                for j in range(i + 1, len(arcs)):
                    if _crosses(arcs[i], arcs[j]):
                        violations.append(
                            f"x={x}: {side_name}-arcs {arcs[i]} and {arcs[j]} interleave"
                        )
            far = bodies.get(body_cell(x), ())
            for a0, a1 in arcs:
                lo, hi = sorted((a0, a1))
                for r in far:
                    if lo < r < hi:
                        violations.append(
                            f"x={x}: {side_name}-arc ({lo},{hi}) encloses body rank {r}"
                        )
    return (not violations, violations)


# -----------------------------------------------------------------------------------
# Transition
# -----------------------------------------------------------------------------------

def fold_goes_over(label: str, orient_before: int) -> bool:
    """Does the moving flap land on top? Derived in the module docstring."""
    return (label == VALLEY) == (orient_before > 0)


def apply_fold(state: StripState, crease: int, side: int) -> StripState | None:
    """Pure transition. Returns the new state, or None if the fold is illegal.

    Illegal means: the crease is already folded, or the resulting configuration would
    push paper through paper.
    """
    candidate = fold_unchecked(state, crease, side)
    if candidate is None:
        return None
    return candidate if check_no_crossing(candidate)[0] else None


def fold_unchecked(state: StripState, crease: int, side: int) -> StripState | None:
    """Geometry of the fold with the legality check omitted.

    Exposed so the tests can ask both checkers about configurations that ``apply_fold``
    rejects; a rejected candidate still has to be a well-formed state to be judged.
    Returns None only when the crease is already folded, which has no geometry at all.
    """
    if not 0 <= crease < state.n - 1 or side not in (SIDE_LEFT, SIDE_RIGHT):
        raise ValueError(f"bad action ({crease}, {side}) for n={state.n}")
    if state.is_folded(crease):
        return None

    moving = (
        range(0, crease + 1) if side == SIDE_LEFT else range(crease + 1, state.n)
    )
    moving_set = set(moving)
    m_seg = crease if side == SIDE_LEFT else crease + 1
    orient_before = state.orient[m_seg]
    over = fold_goes_over(state.mv[crease], orient_before)

    x0 = state.crease_boundary(crease)
    pos = list(state.pos)
    orient = list(state.orient)
    for s in moving_set:
        pos[s] = 2 * x0 - pos[s] - 1
        orient[s] = -orient[s]

    new_folded = state.folded | (1 << crease)
    n_panels = bin(new_folded).count("1") + 1

    # Rebuild the total order. Stationary panels keep their relative order; moving
    # panels keep theirs but reversed (a flipped stack is upside down); the moving
    # block goes entirely above (over) or entirely below (under) the stationary one.
    old_rank_of_new_panel: list[int] = []
    is_moving: list[bool] = []
    for p in range(n_panels):
        seg = next(
            s for s in range(state.n)
            if bin(new_folded & ((1 << s) - 1)).count("1") == p
        )
        old_rank_of_new_panel.append(state.panel_rank[state.panel_of(seg)])
        is_moving.append(seg in moving_set)

    stationary = sorted(
        (p for p in range(n_panels) if not is_moving[p]),
        key=lambda p: old_rank_of_new_panel[p],
    )
    movers = sorted(
        (p for p in range(n_panels) if is_moving[p]),
        key=lambda p: old_rank_of_new_panel[p],
        reverse=True,
    )
    bottom_to_top = stationary + movers if over else movers + stationary

    panel_rank = [0] * n_panels
    for rank, p in enumerate(bottom_to_top):
        panel_rank[p] = rank

    shift = min(pos)
    return StripState(
        n=state.n,
        mv=state.mv,
        pos=tuple(p - shift for p in pos),
        orient=tuple(orient),
        panel_rank=tuple(panel_rank),
        folded=new_folded,
        step=state.step + 1,
    )


def legal_actions(state: StripState) -> list[int]:
    return [a for a in range(action_size(state.n)) if apply_fold(state, *decode(a)) is not None]


# -----------------------------------------------------------------------------------
# Action codec
# -----------------------------------------------------------------------------------

def action_size(n: int) -> int:
    return 2 * (n - 1)


def encode(crease: int, side: int) -> int:
    return crease * 2 + side


def decode(action: int) -> tuple[int, int]:
    return divmod(action, 2)


# -----------------------------------------------------------------------------------
# alpha-zero-general-shaped single-player Game interface
# -----------------------------------------------------------------------------------

DEAD_END_FLOOR = -1.0
DEAD_END_RANGE = 0.5  # dead-end scores live in [-1.0, -0.5], never near the 0 sentinel


class StripGame:
    """Single-player Game over 1-D strips, method names per alpha-zero-general.

    ``player`` is pinned to 1, ``getCanonicalForm`` is the identity, and
    ``getGameEnded`` returns a continuous score in [-1, 1] where 0.0 keeps its upstream
    meaning of "not terminal" -- so terminal scores are clamped away from zero.
    """

    def __init__(self, mv: tuple[str, ...]):
        self.mv = tuple(mv)
        self.n = len(self.mv) + 1

    def getInitBoard(self) -> StripState:
        return initial_state(self.mv)

    def getBoardSize(self) -> tuple[int, int]:
        return (self.n, 5)  # per-segment feature rows; see net.py

    def getActionSize(self) -> int:
        return action_size(self.n)

    def getNextState(self, state: StripState, player: int, action: int):
        nxt = apply_fold(state, *decode(action))
        if nxt is None:
            raise ValueError(f"illegal action {action}")
        return nxt, 1

    def getValidMoves(self, state: StripState, player: int = 1) -> list[int]:
        valid = [0] * self.getActionSize()
        for a in legal_actions(state):
            valid[a] = 1
        return valid

    def getGameEnded(self, state: StripState, player: int = 1) -> float:
        if state.is_solved:
            return 1.0
        if any(self.getValidMoves(state)):
            return 0.0
        progress = state.n_folded / (self.n - 1)
        return DEAD_END_FLOOR + DEAD_END_RANGE * progress

    def getCanonicalForm(self, state: StripState, player: int = 1) -> StripState:
        return state

    def getSymmetries(self, state: StripState, pi):
        return [(state, pi)]

    def stringRepresentation(self, state: StripState) -> str:
        """Hashable key. Includes the layer stack: two states with the same folded
        silhouette but different stacking are different states."""
        ranks = tuple(state.rank_of(s) for s in range(state.n))
        return f"{state.pos}|{state.orient}|{ranks}|{state.folded}"
