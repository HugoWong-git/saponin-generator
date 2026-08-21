"""Correctness tests for the 2-D map-folding environment.

The load-bearing tests here are the two degenerate-axis equivalences. A 1 x n grid and
an m x 1 grid must behave *exactly* like `smoke_test.strip`, which is a separately
written and separately verified implementation. Walking both state spaces in lockstep
compares geometry, layer ranks and legality on every reachable state, so a disagreement
anywhere shows up as a failure. That is stronger evidence than any assertion written
against the 2-D code's own idea of what it should do.

The n range is capped here to keep the suite quick; the full sweep to n=8 (64,618
states per axis) is what was actually run, and re-running it is a one-line change.
"""

from __future__ import annotations

import itertools

import pytest

from grid2d import grid as G
from grid2d.instances import maekawa_ok, make_set
from smoke_test import strip as S


def _strip_key(st):
    return (st.pos, st.orient, tuple(st.rank_of(s) for s in range(st.n)), st.folded)


def _row_key(gs):
    return (gs.xpos, gs.oxs, tuple(gs.rank(0, c) for c in range(gs.n)), gs.vfolded)


def _col_key(gs):
    return (gs.ypos, gs.oys, tuple(gs.rank(r, 0) for r in range(gs.m)), gs.hfolded)


def _lockstep(mv, build, key, axis, size):
    """Walk strip and grid state spaces together; assert they never diverge."""
    s0 = S.initial_state(mv)
    g0 = build(mv)
    stack = [(s0, g0)]
    seen = {(_strip_key(s0), key(g0))}
    while stack:
        s, g = stack.pop()
        assert _strip_key(s) == key(g), f"state diverged for {mv}"
        for k in range(size - 1):
            for side in (0, 1):
                sn = S.apply_fold(s, k, side)
                gn = G.apply_fold(g, axis, k, side)
                assert (sn is None) == (
                    gn is None
                ), f"legality diverged for {mv} at crease {k} side {side}"
                if sn is None:
                    continue
                pair = (_strip_key(sn), key(gn))
                if pair not in seen:
                    seen.add(pair)
                    stack.append((sn, gn))


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_single_row_matches_strip(n):
    """A 1 x n grid is the 1-D strip. Every reachable state must agree."""
    for mv in itertools.product("MV", repeat=n - 1):
        _lockstep(mv, lambda mv: G.initial_state((), (mv,)), _row_key, G.AXIS_V, n)


@pytest.mark.parametrize("m", [2, 3, 4, 5, 6])
def test_single_column_matches_strip(m):
    """An m x 1 grid is the strip transposed, exercising the horizontal code path."""
    for mv in itertools.product("MV", repeat=m - 1):
        _lockstep(
            mv,
            lambda mv: G.initial_state(
                tuple((lab,) for lab in mv), tuple(() for _ in range(len(mv) + 1))
            ),
            _col_key,
            G.AXIS_H,
            m,
        )


def test_initial_state_is_flat_and_unfolded():
    hmv, vmv = (("V", "V"),), (("V",), ("M",))
    s = G.initial_state(hmv, vmv)
    assert (s.m, s.n) == (2, 2)
    assert s.n_folded == 0 and not s.is_solved
    assert G.check_no_crossing(s)[0]
    assert all(s.face(r, c) == 1 for r in range(2) for c in range(2))


def test_transition_is_pure():
    """apply_fold must never mutate its input; MCTS depends on it."""
    hmv, vmv = (("V", "M"),), (("V",), ("V",))
    s = G.initial_state(hmv, vmv)
    before = (s.xpos, s.oxs, s.ypos, s.oys, s.panel_rank, s.vfolded, s.hfolded)
    for a in G.legal_actions(s):
        G.apply_fold(s, *G.decode(s.m, s.n, a))
    assert (s.xpos, s.oxs, s.ypos, s.oys, s.panel_rank, s.vfolded, s.hfolded) == before


def test_label_disagreement_blocks_the_fold():
    """The 2-D constraint: one rigid fold cannot realise two different labels.

    A vertical crease whose two row segments demand opposite labels has no single
    over/under bit that satisfies both, so the fold is unavailable from the flat state.
    """
    s = G.initial_state((("V", "V"),), (("V",), ("M",)))
    assert G.required_over(s, G.AXIS_V, 0, 0) is None
    assert G.fold_unchecked(s, G.AXIS_V, 0, 0) is None
    assert G.apply_fold(s, G.AXIS_V, 0, 0) is None

    agree = G.initial_state((("V", "V"),), (("V",), ("V",)))
    assert G.required_over(agree, G.AXIS_V, 0, 0) is not None
    assert G.apply_fold(agree, G.AXIS_V, 0, 0) is not None


def test_already_folded_crease_is_rejected():
    s = G.initial_state((("V", "V"),), (("V",), ("V",)))
    once = G.apply_fold(s, G.AXIS_V, 0, 0)
    assert once is not None and once.is_folded(G.AXIS_V, 0)
    assert G.apply_fold(once, G.AXIS_V, 0, 0) is None
    assert G.apply_fold(once, G.AXIS_V, 0, 1) is None


def test_bad_action_raises():
    s = G.initial_state((("V", "V"),), (("V",), ("V",)))
    with pytest.raises(ValueError):
        G.fold_unchecked(s, G.AXIS_V, 5, 0)
    with pytest.raises(ValueError):
        G.fold_unchecked(s, G.AXIS_V, 0, 7)


def test_action_codec_is_a_bijection():
    for m, n in ((2, 2), (3, 5), (6, 14)):
        seen = set()
        for a in range(G.action_size(m, n)):
            axis, k, side = G.decode(m, n, a)
            assert G.encode(m, n, axis, k, side) == a
            seen.add((axis, k, side))
        assert len(seen) == G.action_size(m, n)


def test_string_representation_separates_stacking():
    """Same silhouette, different stack, must not collide in the transposition table."""
    s = G.initial_state((("V", "V"),), (("V",), ("V",)))
    game = G.GridGame(s.hmv, s.vmv)
    low = G.apply_fold(s, G.AXIS_V, 0, 0)
    high = G.apply_fold(s, G.AXIS_V, 0, 1)
    assert low is not None and high is not None
    assert low.xpos == high.xpos  # same folded silhouette
    assert game.stringRepresentation(low) != game.stringRepresentation(high)


def test_derived_instances_are_solvable_and_locally_valid():
    """Generation guarantee, and a real theorem showing up empirically.

    Every instance derived from a physical fold sequence must satisfy Maekawa at every
    interior vertex -- a fold sequence cannot produce a locally invalid pattern.
    """
    for m, n in ((3, 3), (4, 4)):
        instances = make_set(m, n, 12, seed=5, family="derived")
        assert instances, "generator produced nothing"
        for hmv, vmv in instances:
            assert maekawa_ok(hmv, vmv)
            game = G.GridGame(hmv, vmv)
            assert _solvable(game), f"derived instance not solvable: {hmv} {vmv}"


def test_maekawa_valid_is_not_sufficient():
    """The parent project's headline claim, demonstrated rather than cited.

    Local theorems are necessary, not sufficient: some grids satisfy Maekawa at every
    interior vertex and still admit no legal fold sequence at all.
    """
    unsolvable = 0
    for m, n in ((3, 3), (2, 4), (4, 4)):
        for hmv, vmv in make_set(m, n, 25, seed=1, family="maekawa"):
            assert maekawa_ok(hmv, vmv)
            if not _solvable(G.GridGame(hmv, vmv)):
                unsolvable += 1
    assert unsolvable > 0, "expected some locally-valid but globally unfoldable grids"


def test_terminal_score_never_collides_with_the_not_terminal_sentinel():
    """0.0 means 'not terminal' upstream, so genuine terminal scores must avoid it."""
    for hmv, vmv in make_set(4, 4, 20, seed=9, family="maekawa"):
        game = G.GridGame(hmv, vmv)
        seen, stack = set(), [game.getInitBoard()]
        while stack:
            s = stack.pop()
            key = game.stringRepresentation(s)
            if key in seen:
                continue
            seen.add(key)
            actions = G.legal_actions(s)
            score = game.getGameEnded(s)
            if s.is_solved or not actions:
                assert score != 0.0
            else:
                assert score == 0.0
            for a in actions:
                nxt = G.apply_fold(s, *G.decode(s.m, s.n, a))
                if nxt is not None:
                    stack.append(nxt)


def _solvable(game: G.GridGame) -> bool:
    seen: set[str] = set()

    def dfs(state) -> bool:
        if state.is_solved:
            return True
        key = game.stringRepresentation(state)
        if key in seen:
            return False
        seen.add(key)
        for a in G.legal_actions(state):
            nxt = G.apply_fold(state, *G.decode(state.m, state.n, a))
            if nxt is not None and dfs(nxt):
                return True
        return False

    return dfs(game.getInitBoard())
