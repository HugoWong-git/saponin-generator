import os, sys, torch, torch.nn as nn, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv import load

class RNN(nn.Module):
    def __init__(self, nv, p):
        super().__init__()
        self._embedding = nn.Embedding(nv, p["embedding_layer_size"])
        self._rnn = nn.LSTM(p["embedding_layer_size"], p["layer_size"],
                            num_layers=p["num_layers"], batch_first=True,
                            dropout=p["dropout"])
        self._linear = nn.Linear(p["layer_size"], nv)
    def forward(self, x, h=None):
        e = self._embedding(x)
        o, h = self._rnn(e, h)
        return self._linear(o), h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prior"); ap.add_argument("-n", type=int, default=10000)
    ap.add_argument("--temp", type=float, default=1.0)
    ap.add_argument("--maxlen", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    d = load(a.prior)
    vocab = d["vocabulary"]["tokens"]
    inv = {v: k for k, v in vocab.items()}
    nv = len(vocab)
    maxlen = a.maxlen or d["max_sequence_length"]
    BOS, EOS, PAD = vocab["^"], vocab["$"], vocab["$"]

    m = RNN(nv, d["network_params"]); m.load_state_dict(d["network"]); m.eval()
    torch.manual_seed(a.seed)

    out = []
    hit_cap = 0
    with torch.no_grad():
        done_total = 0
        while done_total < a.n:
            B = min(a.batch, a.n - done_total)
            x = torch.full((B, 1), BOS, dtype=torch.long)
            h = None
            seqs = [[] for _ in range(B)]
            finished = torch.zeros(B, dtype=torch.bool)
            for step in range(maxlen - 1):
                logits, h = m(x, h)
                logits = logits[:, -1, :] / a.temp
                probs = torch.softmax(logits, dim=-1)
                nxt = torch.multinomial(probs, 1).squeeze(1)
                nxt = torch.where(finished, torch.full_like(nxt, PAD), nxt)
                for i in range(B):
                    if not finished[i] and nxt[i].item() != EOS:
                        seqs[i].append(inv[nxt[i].item()])
                finished = finished | (nxt == EOS)
                if finished.all(): break
                x = nxt.unsqueeze(1)
            hit_cap += int((~finished).sum().item())
            out.extend("".join(s) for s in seqs)
            done_total += B
            print(f"  sampled {done_total}/{a.n}", file=sys.stderr)

    with open(a.out, "w") as f:
        for s in out: f.write(s + "\n")
    print(f"wrote {len(out)} raw strings to {a.out}")
    print(f"hit the {maxlen}-token cap without emitting EOS: {hit_cap} ({100*hit_cap/len(out):.2f}%)")

main()
