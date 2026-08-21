"""Single-player MCTS (SP-MCTS).

Follows the SP-MCTS selection rule (Schadd et al.), which augments UCT with the maximum
reward seen in a subtree and the reward variance:

    score(a) = mean(a) + c * sqrt(ln N / n_a)
             + w_max * max(a)
             + sqrt((sum_sq(a) - n_a * mean(a)^2 + D) / n_a)

The extra terms matter because the goal here is *one* best fold sequence, not robust
average play: a branch that usually fails but sometimes reaches a full fold is worth
more than a branch that reliably half-folds.  Plain UCT averages that signal away.

Runs with or without a policy/value network.  With no network, priors are uniform and
leaf values come from a uniform random rollout.  With one, priors come from the policy
head and the leaf value blends the value head with a rollout drawn from the policy head.
Both arms therefore spend their expansion budget on the same things, so a difference
between them is attributable to the learning and not to the presence of rollouts.

De-adversarialised: no sign flips on the value backup and no player alternation.
"""

from __future__ import annotations

import math
import random

from .strip import StripGame, StripState, apply_fold, decode

C_PUCT = 1.4
W_MAX = 1.0
D_VARIANCE = 1.0
FPU_VALUE = 0.0  # assumed value of an unvisited child; see the note in search()


class SPMCTS:
    def __init__(
        self,
        game: StripGame,
        net=None,
        c_puct: float = C_PUCT,
        w_max: float = W_MAX,
        d_var: float = D_VARIANCE,
        rng: random.Random | None = None,
    ):
        self.game = game
        self.net = net
        self.c_puct = c_puct
        self.w_max = w_max
        self.d_var = d_var
        self.rng = rng or random.Random(0)

        self.N: dict[tuple[str, int], int] = {}
        self.W: dict[tuple[str, int], float] = {}
        self.W2: dict[tuple[str, int], float] = {}
        self.MAXQ: dict[tuple[str, int], float] = {}
        self.Ns: dict[str, int] = {}
        self.Ps: dict[str, list[float]] = {}
        self.Vs: dict[str, list[int]] = {}

        self.expansions = 0
        self.best_score = -math.inf
        self.best_path: list[int] = []
        # Tracked explicitly rather than inferred from a backed-up score: with a net the
        # leaf value blends the rollout with the value head, so a solved rollout no
        # longer arrives as an exact 1.0 and would go unnoticed.
        self.found_solution = False
        self.expansions_at_solution: int | None = None

    # -- helpers ---------------------------------------------------------------------

    def _valid(self, state: StripState, key: str) -> list[int]:
        if key not in self.Vs:
            self.Vs[key] = self.game.getValidMoves(state)
        return self.Vs[key]

    def _priors(self, state: StripState, key: str, valid: list[int]) -> list[float]:
        if key in self.Ps:
            return self.Ps[key]
        if self.net is None:
            raw = [1.0] * len(valid)
        else:
            raw, _ = self.net.predict(state)
        masked = [p * v for p, v in zip(raw, valid)]
        total = sum(masked)
        self.Ps[key] = (
            [p / total for p in masked]
            if total > 0
            else [v / max(1, sum(valid)) for v in valid]
        )
        return self.Ps[key]

    def _leaf_value(self, state: StripState) -> float:
        """Value estimate for a newly expanded leaf.

        Both arms roll out, so the expansion budget buys the same thing in each and the
        only difference between them is whether the net supplies the priors and the
        rollout distribution.  A pure value-head leaf evaluation was tried first and is
        reported in RESULTS.md: at these budgets it cannot reach the depth where
        solutions live, so it never solves anything, and comparing it to a rollout arm
        would have measured the rollout, not the learning.
        """
        rollout = self._rollout(state)
        if self.net is None:
            return rollout
        return 0.5 * rollout + 0.5 * self.net.predict(state)[1]

    def _rollout(self, state: StripState) -> float:
        """Rollout to a terminal state; returns its score.

        Actions are drawn uniformly from the legal moves, or from the policy head
        restricted to them when a net is attached.
        """
        while True:
            score = self.game.getGameEnded(state)
            if score != 0.0:
                self._note_solution(state)
                return score
            valid = self.game.getValidMoves(state)
            choices = [a for a, v in enumerate(valid) if v]
            self.expansions += 1
            if self.net is None:
                action = self.rng.choice(choices)
            else:
                weights = [max(1e-6, self.net.predict(state)[0][a]) for a in choices]
                action = self.rng.choices(choices, weights=weights)[0]
            state = apply_fold(state, *decode(action))

    # -- search ----------------------------------------------------------------------

    def search(self, state: StripState, path: list[int] | None = None) -> float:
        path = path or []
        key = self.game.stringRepresentation(state)

        score = self.game.getGameEnded(state)
        if score != 0.0:
            self._note_solution(state)
            self._record(score, path)
            return score

        valid = self._valid(state, key)
        if key not in self.Ns:
            self._priors(state, key, valid)
            self.Ns[key] = 0
            value = self._leaf_value(state)
            self._record(value, path)
            return value

        priors = self.Ps[key]
        best_a, best_u = -1, -math.inf
        for a, v in enumerate(valid):
            if not v:
                continue
            sa = (key, a)
            # An unvisited child is scored as though it had a single visit worth FPU.
            # Giving unvisited children an infinite bonus instead (the textbook UCT
            # convention) forces a breadth-first sweep of all 2(n-1) root actions before
            # the search descends at all, which at these budgets means never reaching
            # the depth n-1 where solutions live.
            n_a = self.N.get(sa, 0) or 1
            total = self.W.get(sa, FPU_VALUE)
            total_sq = self.W2.get(sa, FPU_VALUE * FPU_VALUE)
            best_seen = self.MAXQ.get(sa, FPU_VALUE)

            mean = total / n_a
            explore = self.c_puct * priors[a] * math.sqrt(self.Ns[key] + 1e-8) / (1 + n_a)
            variance = max(0.0, total_sq - n_a * mean * mean + self.d_var) / n_a
            u = mean + explore + self.w_max * best_seen + math.sqrt(variance)
            if u > best_u:
                best_u, best_a = u, a

        self.expansions += 1
        nxt = apply_fold(state, *decode(best_a))
        value = self.search(nxt, path + [best_a])

        sa = (key, best_a)
        self.N[sa] = self.N.get(sa, 0) + 1
        self.W[sa] = self.W.get(sa, 0.0) + value
        self.W2[sa] = self.W2.get(sa, 0.0) + value * value
        self.MAXQ[sa] = max(self.MAXQ.get(sa, -math.inf), value)
        self.Ns[key] += 1
        return value

    def _note_solution(self, state: StripState) -> None:
        if state.is_solved and not self.found_solution:
            self.found_solution = True
            self.expansions_at_solution = self.expansions

    def _record(self, score: float, path: list[int]) -> None:
        if score > self.best_score:
            self.best_score, self.best_path = score, list(path)

    def run(self, state: StripState, budget: int) -> bool:
        """Search until ``budget`` expansions are spent or a solution is found.

        Returns True if a fully-folded state was reached.
        """
        while self.expansions < budget:
            self.search(state)
            if self.found_solution:
                return True
        return self.found_solution

    def policy(self, state: StripState, temperature: float = 1.0) -> list[float]:
        """Visit-count distribution at ``state``, for self-play training targets."""
        key = self.game.stringRepresentation(state)
        counts = [self.N.get((key, a), 0) for a in range(self.game.getActionSize())]
        total = sum(counts)
        if total == 0:
            valid = self.game.getValidMoves(state)
            k = sum(valid)
            return [v / k for v in valid]
        if temperature == 0:
            best = max(range(len(counts)), key=lambda a: counts[a])
            out = [0.0] * len(counts)
            out[best] = 1.0
            return out
        adjusted = [c ** (1.0 / temperature) for c in counts]
        z = sum(adjusted)
        return [a / z for a in adjusted]


def random_arm(game: StripGame, state: StripState, budget: int, rng: random.Random):
    """Baseline: repeated random legal rollouts from the root until budget is spent."""
    expansions = 0
    while expansions < budget:
        cur = state
        while True:
            score = game.getGameEnded(cur)
            if score != 0.0:
                break
            valid = game.getValidMoves(cur)
            choices = [a for a, v in enumerate(valid) if v]
            expansions += 1
            cur = apply_fold(cur, *decode(rng.choice(choices)))
            if expansions >= budget:
                break
        if cur.is_solved:
            return True, expansions
    return False, expansions
