"""Tests for the transition function and the layer-crossing check.

Includes deliberately-broken cases that must be rejected: a hand-worked illegal fold, a
hand-built crossing configuration, and a state pair that differs only in stacking.
"""

from __future__ import annotations

import itertools

import pytest

from smoke_test.brute_force import explore, solve
from smoke_test.strip import (
    MOUNTAIN,
    SIDE_LEFT,
    SIDE_RIGHT,
    VALLEY,
    StripGame,
    StripState,
    action_size,
    apply_fold,
    check_no_crossing,
    decode,
    encode,
    fold_goes_over,
    fold_unchecked,
    initial_state,
    legal_actions,
)
from smoke_test.verify import geometric_no_crossing


# -- action codec -------------------------------------------------------------------

def test_action_codec_is_a_bijection():
    for n in (2, 6, 12):
        seen = {decode(a) for a in range(action_size(n))}
        assert len(seen) == action_size(n)
        for crease, side in seen:
            assert encode(crease, side) in range(action_size(n))
            assert decode(encode(crease, side)) == (crease, side)


# -- over/under is pinned by the label, not chosen --------------------------------

@pytest.mark.parametrize(
    "label,orient,expected_over",
    [
        (VALLEY, 1, True),     # face-up pair, flap over the top -> top faces meet
        (VALLEY, -1, False),
        (MOUNTAIN, 1, False),  # face-up pair, flap under -> bottom faces meet
        (MOUNTAIN, -1, True),
    ],
)
def test_fold_direction_is_determined_by_label_and_orientation(label, orient, expected_over):
    assert fold_goes_over(label, orient) is expected_over


def test_first_fold_of_a_pair_stacks_the_right_way_round():
    """n=2: a valley puts the mover on top; a mountain puts it underneath."""
    valley = apply_fold(initial_state((VALLEY,)), 0, SIDE_LEFT)
    assert valley.rank_of(0) > valley.rank_of(1)
    mountain = apply_fold(initial_state((MOUNTAIN,)), 0, SIDE_LEFT)
    assert mountain.rank_of(0) < mountain.rank_of(1)


# -- purity -------------------------------------------------------------------------

def test_transition_is_pure():
    state = initial_state((VALLEY, MOUNTAIN, VALLEY))
    before = (state.pos, state.orient, state.panel_rank, state.folded, state.step)
    apply_fold(state, 1, SIDE_RIGHT)
    assert (state.pos, state.orient, state.panel_rank, state.folded, state.step) == before


def test_refolding_a_folded_crease_is_rejected():
    state = apply_fold(initial_state((VALLEY, VALLEY)), 0, SIDE_LEFT)
    assert state.is_folded(0)
    assert apply_fold(state, 0, SIDE_LEFT) is None
    assert apply_fold(state, 0, SIDE_RIGHT) is None


# -- the deliberately-broken cases --------------------------------------------------

def test_hand_worked_illegal_fold_is_rejected():
    """n=4 'MMM': fold crease 1 left, then crease 0 left, is physically impossible.

    After the first fold the stack in cell 0 is seg1 (bottom), seg2 (middle) and cell 1
    holds seg0, seg3.  Folding crease 0 to the left would run paper from seg1 at the
    bottom, around the right edge at x=1, up to seg0 at the top -- straight through
    seg3, which sticks out past x=1 at the middle level.
    """
    state = apply_fold(initial_state((MOUNTAIN,) * 3), 1, SIDE_LEFT)
    assert state is not None
    candidate = fold_unchecked(state, 0, SIDE_LEFT)
    ok, violations = check_no_crossing(candidate)
    assert not ok
    assert "encloses body rank" in violations[0]
    assert apply_fold(state, 0, SIDE_LEFT) is None
    assert not geometric_no_crossing(candidate)


def test_hand_built_crossing_state_is_rejected():
    """Two interleaving hairpins at the same boundary: seg0-seg1 wraps ranks (0,2) and
    seg2-seg3 wraps ranks (1,3). Nested would be fine; interleaved is paper through
    paper."""
    crossing = StripState(
        n=4,
        mv=(VALLEY,) * 3,
        pos=(0, 0, 0, 0),
        orient=(1, -1, 1, -1),
        panel_rank=(0, 2, 1, 3),
        folded=0b111,
        step=3,
    )
    ok, violations = check_no_crossing(crossing)
    assert not ok
    assert "interleave" in " ".join(violations)
    assert not geometric_no_crossing(crossing)


def test_nested_hairpins_are_accepted():
    """The same shape with ranks nested rather than interleaved is legal."""
    nested = StripState(
        n=4,
        mv=(VALLEY,) * 3,
        pos=(0, 0, 0, 0),
        orient=(1, -1, 1, -1),
        panel_rank=(0, 3, 1, 2),
        folded=0b111,
        step=3,
    )
    assert check_no_crossing(nested)[0]
    assert geometric_no_crossing(nested)


def test_string_representation_separates_states_that_differ_only_in_stacking():
    game = StripGame((VALLEY,))
    over = apply_fold(game.getInitBoard(), 0, SIDE_LEFT)
    under = apply_fold(initial_state((MOUNTAIN,)), 0, SIDE_LEFT)
    assert over.pos == under.pos  # identical folded silhouette
    assert game.stringRepresentation(over) != game.stringRepresentation(under)


# -- P1: the two checkers agree, on accepted and rejected candidates alike ----------

@pytest.mark.parametrize("n", [3, 4, 5, 6])
def test_combinatorial_and_geometric_checks_agree_everywhere(n):
    checked = 0
    for mv in itertools.product("MV", repeat=n - 1):
        for state in explore(tuple(mv), collect=True)[1]:
            for a in range(action_size(n)):
                candidate = fold_unchecked(state, *decode(a))
                if candidate is None:
                    continue
                assert check_no_crossing(candidate)[0] == geometric_no_crossing(candidate)
                checked += 1
    assert checked > 0


# -- P1: the environment solves what the oracle says is solvable -------------------

@pytest.mark.parametrize("n", [4, 5, 6, 7])
def test_every_pattern_is_solvable_and_takes_exactly_n_minus_1_folds(n):
    for mv in itertools.product("MV", repeat=n - 1):
        result = solve(tuple(mv))
        assert result.complete
        assert result.solvable
        assert result.min_folds == n - 1


def test_solved_states_have_every_crease_folded_and_one_cell():
    for mv in itertools.product("MV", repeat=4):
        for state in explore(tuple(mv), collect=True)[1]:
            if state.is_solved:
                assert state.n_folded == state.n - 1
                assert len(set(state.pos)) == 1
                assert len({state.rank_of(s) for s in range(state.n)}) == state.n


def test_game_ended_never_returns_the_not_terminal_sentinel_at_a_terminal_state():
    for mv in itertools.product("MV", repeat=5):
        game = StripGame(tuple(mv))
        for state in explore(tuple(mv), collect=True)[1]:
            score = game.getGameEnded(state)
            terminal = state.is_solved or not legal_actions(state)
            assert (score != 0.0) == terminal
            assert -1.0 <= score <= 1.0
