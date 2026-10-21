# GPU evaluation harness for the fx2-cmix-transformer model (T4-compatible).
# Data: /root/hp/data/tok.u8 (vocab indices), bounds.i32 (article boundaries),
#       prior.cnt/.idx/.val (sparse PPMD priors, entries >= 0.0007 kept).
import sys, os, math, time
import numpy as np
import torch
import torch.nn.functional as F

REPO = '/root/hp_round9/restored/src/fx2-cmix-transformer-v1'
sys.path.insert(0, REPO)
import pysrc.model as M
from pysrc.model import Transformer, TransformerConfig, MatmulQuantization
from pysrc.quantization import Quantization

D = '/root/hp/data'
V = 205
MAX_PIECE = 1 << 17


# ---------------------------------------------------------------- attention
def windowed_attention(args):
    """Exact sliding-window causal attention with document masking, chunked so
    it never materialises a T x T mask (works on T4 / any GPU)."""
    q, k, v = args.queries, args.keys, args.values
    B, T, H, Dh = q.shape
    assert B == 1
    W = int(args.window_size) if args.window_size is not None else T
    scale = args.scale if args.scale is not None else Dh ** -0.5
    dev = q.device
    if args.cumulative_sequence_lengths is not None:
        cu = args.cumulative_sequence_lengths[0].to(torch.int64)
        doc = torch.searchsorted(cu, torch.arange(T, device=dev), right=True)
    else:
        doc = torch.zeros(T, dtype=torch.int64, device=dev)
    out = torch.empty_like(q)
    C = 1024
    for s in range(0, T, C):
        e = min(T, s + C)
        ks = max(0, s - W + 1)
        qi = torch.arange(s, e, device=dev)[:, None]
        kj = torch.arange(ks, e, device=dev)[None, :]
        mask = (kj <= qi) & (qi - kj < W) & (doc[s:e, None] == doc[None, ks:e])
        o = F.scaled_dot_product_attention(
            q[:, s:e].transpose(1, 2), k[:, ks:e].transpose(1, 2),
            v[:, ks:e].transpose(1, 2), attn_mask=mask, scale=scale)
        out[:, s:e] = o.transpose(1, 2)
    return out


M.attention_function = windowed_attention


# ---------------------------------------------------------------- model
def make_config(quantized=True, dtype=torch.float32, **over):
    wq = Quantization(buckets=15, block_size=None, scale_dtype=torch.bfloat16,
                      arithmetic_dtype=torch.float32, scale_init="scaled_max", epsilon=None)
    aq = Quantization(buckets=256, block_size=None, scale_dtype=torch.bfloat16,
                      arithmetic_dtype=torch.float32, scale_init="scaled_mean", epsilon=None)
    mq = MatmulQuantization(weight=wq, activation=aq) if quantized else None
    kw = dict(
        vocabulary_size=205, prior_embedding=True, prior_logit_mixing=False,
        max_variable_sequence_length=None, n_layers=12,
        attention_weight_sharing_pattern=list(range(12)), mlp_weight_sharing_pattern=list(range(12)),
        d_model=192, kimi_linear=[True, True, True, False] * 3, window_size=1024,
        window_size_multipliers=None, n_query_heads=3, n_key_value_heads=3, d_head=64, d_mla=None,
        rope_base=10_000, half_truncate_rope=False, query_key_norm=True, query_key_norm_gain=False,
        kimi_linear_d_head=64, kimi_linear_n_heads=3, kimi_linear_convolution_size=4,
        value_embedding_pattern=None, prior_value_embedding=False, attention_scale=None,
        d_mlp=768, activation_function="relu_squared", embedding_norm=True, prior_embedding_norm=True,
        skip_connections=True, token_embedding_connections=True, prior_embedding_connections=False,
        dropout=0.0, logit_softcap=15.0, prior_logprob_cap=-12.0, prior_embedding_on_logprobs=False,
        gradient_checkpointing=False, embedding_init="normal", prior_embedding_init="normal",
        up_init="kaiming_uniform", down_init="kaiming_uniform", unembedding_init="kaiming_uniform",
        convolution_init="kaiming_uniform", logit_mixing_head_init="zero",
        activation_dtype=dtype, attention_dtype=dtype, logit_dtype=torch.float32, weight_dtype=torch.float32,
        mlp_quantization=mq, attention_full_rank_quantization=mq, attention_low_rank_quantization=mq,
        qkv_quantization=aq if quantized else None,
        kimi_linear_full_rank_quantization=mq, kimi_linear_low_rank_quantization=mq,
        kimi_linear_beta_projection_quantization=None, kimi_linear_convolution_quantization=None,
        embedding_quantization=wq if quantized else None, prior_embedding_quantization=mq,
        unembedding_quantization=mq, logit_mixing_head_quantization=None,
        adamw_quantization_scales=True, attention_implementation="sdpa")
    kw.update(over)
    return TransformerConfig(**kw)


def load_model(ckpt=REPO + '/models/6m-q4-fp32.tch', device='cuda', quantized=True, strict=True):
    model = Transformer(make_config(quantized=quantized)).to(device)
    sd = torch.load(ckpt, map_location=device)
    missing = model.load_state_dict(sd, strict=strict)
    model.eval()
    return model


# ---------------------------------------------------------------- data
class Data:
    def __init__(self, n_tokens_avail=None):
        self.tok = np.memmap(D + '/tok.u8', dtype=np.uint8, mode='r')
        self.bounds = np.fromfile(D + '/bounds.i32', dtype=np.int32).astype(np.int64)
        self.cnt = np.memmap(D + '/prior.cnt', dtype=np.uint8, mode='r')
        self.idx = np.memmap(D + '/prior.idx', dtype=np.uint8, mode='r')
        self.val = np.memmap(D + '/prior.val', dtype=np.float16, mode='r')
        self.ntok_prior = len(self.cnt)
        # entry offset at every article boundary (cumsum in chunks)
        nb = len(self.bounds)
        self.boff = np.zeros(nb, dtype=np.int64)
        pos = 0; acc = 0; bi = 1
        CH = 1 << 26
        b = self.bounds
        while bi < nb and b[bi] <= self.ntok_prior:
            # advance to b[bi]
            while pos < b[bi]:
                e = min(b[bi], pos + CH)
                acc += int(self.cnt[pos:e].sum(dtype=np.int64))
                pos = e
            self.boff[bi] = acc
            bi += 1
        self.n_art_avail = bi - 1   # articles whose priors are fully available
        # pieces: articles split at MAX_PIECE like the training loader / C++
        self.n_articles = nb - 1

    def article(self, a):
        """returns (tokens int64 [L], dense priors float32 [L, V]) for article a."""
        s, e = int(self.bounds[a]), int(self.bounds[a + 1])
        t = np.asarray(self.tok[s:e], dtype=np.int64)
        c = np.asarray(self.cnt[s:e], dtype=np.int64)
        o0, o1 = int(self.boff[a]), int(self.boff[a + 1])
        ii = np.asarray(self.idx[o0:o1], dtype=np.int64)
        vv = np.asarray(self.val[o0:o1], dtype=np.float32)
        rows = np.repeat(np.arange(e - s), c)
        P = np.zeros((e - s, V), dtype=np.float32)
        P[rows, ii] = vv
        return t, P


def pieces_of(L):
    out = []; s = 0
    while s < L:
        e = min(L, s + MAX_PIECE); out.append((s, e)); s = e
    return out


@torch.no_grad()
def eval_articles(model, data, arts, max_tokens=1 << 17, device='cuda', return_logits=False, hook=None):
    """Returns list of per-token loss arrays (nats); element j of article a's array is the
    loss of predicting token j+1 (only positions 0..L-2 of each piece are predictions)."""
    results = {}
    batch = []; blen = 0

    def flush():
        nonlocal batch, blen
        if not batch:
            return
        toks = np.concatenate([b[1] for b in batch]); pri = np.concatenate([b[2] for b in batch])
        cu = np.cumsum([0] + [len(b[1]) for b in batch]).astype(np.int32)
        x = torch.from_numpy(toks).to(device)[None]
        p = torch.from_numpy(pri).to(device)[None]
        cuq = torch.from_numpy(cu).to(device)[None]
        logits = model.compute_logits(x, p, cuq)[0].float()
        lp = torch.log_softmax(logits, -1)
        for i, (key, t, _) in enumerate(batch):
            s, e = int(cu[i]), int(cu[i + 1])
            tgt = torch.from_numpy(t[1:]).to(device)
            l = -lp[s:e - 1].gather(1, tgt[:, None])[:, 0]
            results[key] = l.cpu().numpy()
            if hook is not None:
                hook(key, lp[s:e - 1], tgt)
        batch = []; blen = 0

    for a in arts:
        t, P = data.article(a)
        for (s, e) in pieces_of(len(t)):
            if e - s < 2:
                results[(a, s)] = np.zeros(0, np.float32); continue
            if blen + (e - s) > max_tokens:
                flush()
            batch.append(((a, s), t[s:e], P[s:e])); blen += e - s
    flush()
    return results

