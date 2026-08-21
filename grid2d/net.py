"""Small policy/value MLP over the map-folding state.

FEATURE DESIGN
--------------
Actions are indexed by *crease line*, not by cell, so the features are per-crease-line
too: one row per vertical line and one per horizontal line, padded to MAX_LINES each.
A per-cell encoding would have to be pooled back down to lines before the policy head
could use it, and at these grid sizes that indirection buys nothing.

The rows carry the two things that decide whether a fold is available:

  * ``consistent_low`` / ``consistent_high`` -- whether the required labels along this
    line currently agree on a single over/under bit, per side. This is the 2-D
    constraint from ``grid.required_over``, handed to the network directly rather than
    left to be rediscovered. It is cheap, exact, and changes as other folds happen.
  * the line's label balance and folded flag, plus the fraction of the *other* axis
    already folded -- the coupling channel. Whether a vertical fold is available depends
    on row orientations, which horizontal folds produce.

Deliberately not a GNN, for the same reason as the 1-D case: a grid's crease graph is a
regular lattice with no interesting structure to message-pass over at these sizes, and
torch-geometric would be a heavyweight dependency for no gain. Noted as a limitation --
this says nothing about whether a GNN would help on an Origamizer-sized irregular graph.

One network serves every grid shape via padding, so it can train on one set of shapes
and be evaluated on others.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .grid import AXIS_H, AXIS_V, MOUNTAIN, GridState, action_size, required_over

MAX_LINES = 14  # per axis; covers every shape used in the experiment
N_FEATURES = 8
POLICY_SIZE = 2 * (2 * MAX_LINES)  # (low, high) for each line of each axis
N_GLOBALS = 4


def _line_row(state: GridState, axis: int, k: int) -> tuple[float, ...]:
    labels = (
        [state.vmv[r][k] for r in range(state.m)]
        if axis == AXIS_V
        else list(state.hmv[k])
    )
    n_mountain = sum(1 for a in labels if a == MOUNTAIN)
    balance = (2 * n_mountain - len(labels)) / max(1, len(labels))
    folded = state.is_folded(axis, k)
    low = required_over(state, axis, k, 0) if not folded else None
    high = required_over(state, axis, k, 1) if not folded else None
    span = (state.n - 1) if axis == AXIS_V else (state.m - 1)
    other_axis_progress = (
        state.n_h_folded / max(1, state.m - 1)
        if axis == AXIS_V
        else state.n_v_folded / max(1, state.n - 1)
    )
    return (
        1.0,                                    # this line exists (padding mask)
        1.0 if axis == AXIS_V else -1.0,
        float(folded),
        balance,
        0.0 if low is None else (1.0 if low else -1.0),
        0.0 if high is None else (1.0 if high else -1.0),
        k / max(1, span),
        other_axis_progress,
    )


def encode_state(state: GridState) -> np.ndarray:
    """Per-crease-line feature rows: vertical lines first, then horizontal."""
    x = np.zeros((2 * MAX_LINES, N_FEATURES), dtype=np.float32)
    for k in range(min(state.n - 1, MAX_LINES)):
        x[k] = _line_row(state, AXIS_V, k)
    for k in range(min(state.m - 1, MAX_LINES)):
        x[MAX_LINES + k] = _line_row(state, AXIS_H, k)
    return x


def encode_globals(state: GridState) -> np.ndarray:
    total = (state.m - 1) + (state.n - 1)
    return np.array(
        [
            state.m / MAX_LINES,
            state.n / MAX_LINES,
            state.n_folded / max(1, total),
            state.step / max(1, total),
        ],
        dtype=np.float32,
    )


def policy_index(state: GridState, action: int) -> int:
    """Map a domain action onto the padded fixed-size policy vector."""
    from .grid import decode

    axis, k, side = decode(state.m, state.n, action)
    base = 0 if axis == AXIS_V else 2 * MAX_LINES
    return base + 2 * k + side


class GridNet(nn.Module):
    def __init__(self, hidden: int = 128):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(2 * MAX_LINES * N_FEATURES + N_GLOBALS, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.policy_head = nn.Linear(hidden, POLICY_SIZE)
        self.value_head = nn.Linear(hidden, 1)

    def forward(self, x, g):
        h = self.body(torch.cat([x.flatten(1), g], dim=1))
        return F.log_softmax(self.policy_head(h), dim=1), torch.tanh(self.value_head(h))


class NetWrapper:
    """Inference + training wrapper; ``predict`` matches what SPMCTS expects."""

    def __init__(self, net: GridNet | None = None, lr: float = 1e-3):
        self.net = net or GridNet()
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=lr)
        self._cache: dict[GridState, tuple[list[float], float]] = {}

    def predict(self, state: GridState) -> tuple[list[float], float]:
        hit = self._cache.get(state)
        if hit is not None:
            return hit
        out = self._predict_uncached(state)
        if len(self._cache) < 200_000:
            self._cache[state] = out
        return out

    def _predict_uncached(self, state: GridState) -> tuple[list[float], float]:
        self.net.eval()
        with torch.no_grad():
            x = torch.from_numpy(encode_state(state)).unsqueeze(0)
            g = torch.from_numpy(encode_globals(state)).unsqueeze(0)
            log_pi, v = self.net(x, g)
        full = torch.exp(log_pi)[0].numpy()
        pi = [
            float(full[policy_index(state, a)])
            for a in range(action_size(state.m, state.n))
        ]
        return pi, float(v.item())

    def train_on(self, examples, epochs: int = 8, batch_size: int = 64) -> float:
        """examples: list of (state, pi over that state's action size, z)."""
        self._cache.clear()
        if not examples:
            return 0.0
        xs = np.stack([encode_state(s) for s, _, _ in examples])
        gs = np.stack([encode_globals(s) for s, _, _ in examples])
        pis = np.zeros((len(examples), POLICY_SIZE), dtype=np.float32)
        for i, (state, pi, _) in enumerate(examples):
            for a, p in enumerate(pi):
                pis[i, policy_index(state, a)] = p
        zs = np.array([z for _, _, z in examples], dtype=np.float32)

        x_t = torch.from_numpy(xs)
        g_t = torch.from_numpy(gs)
        pi_t = torch.from_numpy(pis)
        z_t = torch.from_numpy(zs).unsqueeze(1)

        self.net.train()
        last = 0.0
        for _ in range(epochs):
            perm = torch.randperm(len(examples))
            for i in range(0, len(examples), batch_size):
                idx = perm[i : i + batch_size]
                log_pi, v = self.net(x_t[idx], g_t[idx])
                loss_pi = -(pi_t[idx] * log_pi).sum(dim=1).mean()
                loss_v = F.mse_loss(v, z_t[idx])
                loss = loss_pi + loss_v
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                last = float(loss.item())
        return last

    def save(self, path: str) -> None:
        torch.save(self.net.state_dict(), path)

    def load(self, path: str) -> None:
        self.net.load_state_dict(torch.load(path, map_location="cpu"))
        self._cache.clear()
