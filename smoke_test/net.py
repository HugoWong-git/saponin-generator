"""Small policy/value MLP over the strip state.

Deliberately not a GNN: the parent project's plan calls for one over the crease graph,
but a 1-D strip's graph is a path, so a GNN would buy nothing here that a per-segment
feature stack does not already give.  Adding torch-geometric for a path graph would have
been a heavyweight dependency for no gain -- noted in RESULTS.md.

States of different lengths are padded to MAX_N, so one network serves every n and can
be trained on n=10/12 and evaluated on n=6/8.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .strip import StripState, action_size

MAX_N = 12
N_FEATURES = 7
POLICY_SIZE = action_size(MAX_N)


def encode_state(state: StripState) -> np.ndarray:
    """Per-segment feature rows, padded to MAX_N."""
    x = np.zeros((MAX_N, N_FEATURES), dtype=np.float32)
    n = state.n
    centre = sum(state.pos) / n
    for s in range(min(n, MAX_N)):
        crease_here = s < n - 1
        x[s] = (
            1.0,
            (1.0 if state.mv[s] == "M" else -1.0) if crease_here else 0.0,
            float(state.is_folded(s)) if crease_here else 0.0,
            (state.pos[s] - centre) / n,
            float(state.orient[s]),
            state.rank_of(s) / max(1, n - 1),
            s / max(1, n - 1),
        )
    return x


def encode_globals(state: StripState) -> np.ndarray:
    return np.array(
        [state.n / MAX_N, state.n_folded / max(1, state.n - 1)], dtype=np.float32
    )


class StripNet(nn.Module):
    def __init__(self, hidden: int = 128):
        super().__init__()
        self.body = nn.Sequential(
            nn.Linear(MAX_N * N_FEATURES + 2, hidden),
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

    def __init__(self, net: StripNet | None = None, lr: float = 1e-3):
        self.net = net or StripNet()
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=lr)
        self._cache: dict[StripState, tuple[list[float], float]] = {}

    def predict(self, state: StripState) -> tuple[list[float], float]:
        hit = self._cache.get(state)
        if hit is not None:
            return hit
        out = self._predict_uncached(state)
        if len(self._cache) < 200_000:
            self._cache[state] = out
        return out

    def _predict_uncached(self, state: StripState) -> tuple[list[float], float]:
        self.net.eval()
        with torch.no_grad():
            x = torch.from_numpy(encode_state(state)).unsqueeze(0)
            g = torch.from_numpy(encode_globals(state)).unsqueeze(0)
            log_pi, v = self.net(x, g)
        pi = torch.exp(log_pi)[0].numpy()
        return pi[: action_size(state.n)].tolist(), float(v.item())

    def train_on(self, examples, epochs: int = 8, batch_size: int = 64) -> float:
        self._cache.clear()
        """examples: list of (state, pi over that state's action size, z)."""
        if not examples:
            return 0.0
        xs = np.stack([encode_state(s) for s, _, _ in examples])
        gs = np.stack([encode_globals(s) for s, _, _ in examples])
        pis = np.zeros((len(examples), POLICY_SIZE), dtype=np.float32)
        for i, (_, pi, _) in enumerate(examples):
            pis[i, : len(pi)] = pi
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
