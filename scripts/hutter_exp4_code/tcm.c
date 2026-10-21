/* tcm.c - classical context-mixing coder over DICTIONARY TOKENS (bytes 0-255, group 256-511, member 512-767),
 * optionally blended with a neural model's token distribution. Ideal code lengths.
 *
 * A token is coded as 10 binary decisions, most significant first (the first two bits decide byte/group/member).
 * Contexts: order-0..4 token history, the previous two complete dictionary words, the current position class,
 * a token-level match model, and (test part only) the neural distribution as an extra mixer input.
 *
 * usage: tcm warm_tokens.u16 test_tokens.u16 probs.npy|- out_prefix
 *   tokens are little-endian uint16 files; probs is float16 [n_test, 768]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define TB 22
#define NCTX 9
#define NBIT 10
#define V 768

typedef struct { uint16_t p; uint8_t n; uint8_t c; } Slot;
static float rate[256];
static inline float stretchf(float p) { return logf(p / (1.f - p)); }
static inline float squashf(float x) { if (x > 20) x = 20; if (x < -20) x = -20; return 1.f / (1.f + expf(-x)); }
static unsigned char *readall(const char *fn, size_t *n) {
    FILE *f = fopen(fn, "rb"); if (!f) { perror(fn); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc(*n); if (fread(b, 1, *n, f) != *n) exit(2); fclose(f); return b;
}
static float half2float(uint16_t h) {
    uint32_t s = (h >> 15) & 1, e = (h >> 10) & 31, m = h & 1023, f;
    if (e == 0) { if (!m) f = s << 31; else { e = 127 - 15 + 1; while (!(m & 1024)) { m <<= 1; e--; } m &= 1023; f = (s << 31) | (e << 23) | (m << 13); } }
    else if (e == 31) f = (s << 31) | 0x7f800000 | (m << 13);
    else f = (s << 31) | ((e + 112) << 23) | (m << 13);
    float r; memcpy(&r, &f, 4); return r;
}
typedef struct { uint16_t *t; int idx; } APM;
static void apm_init(APM *a, int n) { a->t = malloc(sizeof(uint16_t) * n * 33); for (int i = 0; i < n; i++) for (int j = 0; j < 33; j++) a->t[i * 33 + j] = (uint16_t)(squashf((j - 16) / 2.f) * 65535); }
static float apm_p(APM *a, float p, int cx) { float s = stretchf(p) * 2 + 16; if (s < 0) s = 0; if (s > 31.999f) s = 31.999f; int lo = (int)s; float w = s - lo; a->idx = cx * 33 + lo + (w > 0.5f); return ((1 - w) * a->t[cx * 33 + lo] + w * a->t[cx * 33 + lo + 1]) / 65536.f; }
static void apm_up(APM *a, int bit) { int g = (bit << 16) + (bit << 5) - bit - bit; a->t[a->idx] += (g - a->t[a->idx]) >> 6; }

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: tcm warm.u16 test.u16 probs.npy|- out_prefix\n"); return 1; }
    size_t nwb, ntb; uint16_t *warm = (uint16_t *)readall(argv[1], &nwb), *test = (uint16_t *)readall(argv[2], &ntb);
    size_t nw = nwb / 2, nt = ntb / 2, n = nw + nt;
    uint16_t *buf = malloc(n * 2); memcpy(buf, warm, nw * 2); memcpy(buf + nw, test, nt * 2);
    const uint16_t *P = NULL;
    if (strcmp(argv[3], "-")) { size_t np; unsigned char *raw = readall(argv[3], &np); uint16_t hl = raw[8] | (raw[9] << 8); P = (const uint16_t *)(raw + 10 + hl); }
    for (int i = 0; i < 256; i++) rate[i] = 1.f / (i + 1.5f);
    Slot *T[NCTX]; for (int i = 0; i < NCTX; i++) { T[i] = calloc((size_t)1 << TB, sizeof(Slot)); for (size_t j = 0; j < ((size_t)1 << TB); j++) T[i][j].p = 32768; }
    const int NIN = NCTX + 3;              /* contexts + match + bias + neural */
    const int NSET = 1024 * 3 * 4;         /* partial-token context x match state x neural confidence */
    float *wA = malloc(sizeof(float) * NIN * NSET), *wB = malloc(sizeof(float) * NIN * NSET);
    for (int i = 0; i < NIN * NSET; i++) { wA[i] = (i % NIN == NCTX + 2) ? 0.f : 0.3f; wB[i] = (i % NIN == NCTX + 2) ? 1.0f : 0.3f; }
    APM apA, apB; apm_init(&apA, 1024 * 4); apm_init(&apB, 1024 * 4);
    /* match model over tokens */
    const int MB = 22, ML = 4; uint32_t *mt = calloc((size_t)1 << MB, 4); size_t mptr = 0; int mlen = 0; float mprob[64]; for (int i = 0; i < 64; i++) mprob[i] = 0.75f;
    double totA = 0, totB = 0, totN = 0;
    float *cA = calloc(nt, 4), *cB = calloc(nt, 4);
    uint32_t w1 = 0, w2 = 0;               /* previous two complete dictionary words (group*256+member) */
    float cum[V + 1];
    for (size_t pos = 0; pos < n; pos++) {
        uint32_t t1 = pos > 0 ? buf[pos - 1] : 0, t2 = pos > 1 ? buf[pos - 2] : 0, t3 = pos > 2 ? buf[pos - 3] : 0, t4 = pos > 3 ? buf[pos - 4] : 0;
        uint32_t cls1 = t1 < 256 ? 0 : (t1 < 512 ? 1 : 2);
        uint32_t h[NCTX];
        h[0] = cls1;
        h[1] = t1 * 0x9e3779b1u + 1;
        h[2] = (t1 * 0x85ebca6bu) ^ (t2 * 0xc2b2ae35u) ^ 2;
        h[3] = (t1 * 0x85ebca6bu) ^ (t2 * 0xc2b2ae35u) ^ (t3 * 0x27d4eb2fu) ^ 3;
        h[4] = (t1 * 0x85ebca6bu) ^ (t2 * 0xc2b2ae35u) ^ (t3 * 0x27d4eb2fu) ^ (t4 * 0x165667b1u) ^ 4;
        h[5] = (w1 * 0x9e3779b1u) ^ (t1 << 8) ^ 5;
        h[6] = (w1 * 0x85ebca6bu) ^ (w2 * 0xc2b2ae35u) ^ (t1 << 4) ^ 6;
        h[7] = (w1 * 0x27d4eb2fu) ^ (cls1 << 28) ^ 7;
        h[8] = (t2 * 0x165667b1u) ^ (cls1 << 24) ^ 8;                  /* skip-1 context */
        /* match model: last occurrence of the previous ML tokens */
        if (pos >= (size_t)ML) {
            uint32_t mh = 0; for (int k = 1; k <= ML; k++) mh = mh * 0x2f0f3ab1u + buf[pos - k] + 1;
            mh >>= (32 - MB);
            if (mlen > 0 && buf[mptr] == buf[pos - 1]) { mptr++; if (mlen < 63) mlen++; }
            else { mlen = 0; mptr = mt[mh]; if (mptr > 0) { while (mlen < 63 && (size_t)mlen < mptr && buf[mptr - 1 - mlen] == buf[pos - 1 - mlen]) mlen++; if (mlen < ML) mlen = 0; } }
            mt[mh] = (uint32_t)pos;
        }
        int expected = mlen > 0 ? buf[mptr] : -1;
        int have = P && pos >= nw;
        if (have) { const uint16_t *r = P + (pos - nw) * V; cum[0] = 0; for (int k = 0; k < V; k++) cum[k + 1] = cum[k] + half2float(r[k]) + 1e-8f; }
        int tok = buf[pos], c0 = 1; double bA = 0, bB = 0, bN = 0;
        for (int b = NBIT - 1; b >= 0; b--) {
            int bit = (tok >> b) & 1; Slot *s[NCTX]; float x[NCTX + 3];
            for (int i = 0; i < NCTX; i++) { uint32_t idx = ((h[i] + c0 * 0x9e3779b1u) * 0x85ebca6bu) >> (32 - TB); s[i] = &T[i][idx]; x[i] = stretchf((s[i]->p + 0.5f) / 65536.f); }
            int eb = -1; float mx = 0;
            if (expected >= 0 && ((expected + 1024) >> (b + 1)) == c0) { eb = (expected >> b) & 1; mx = stretchf(mprob[mlen < 63 ? mlen : 63]) * (eb ? 1 : -1); }
            x[NCTX] = mx; x[NCTX + 1] = 0.25f;
            float pn = 0.5f;
            if (have) {
                int lo = (c0 << (b + 1)) - 1024, wd = 1 << (b + 1), mid = lo + wd / 2;
                int hi = lo + wd; if (lo > V) lo = V; if (mid > V) mid = V; if (hi > V) hi = V;
                float tot = cum[hi] - cum[lo], one = cum[hi] - cum[mid];
                pn = tot > 1e-12f ? one / tot : 0.5f; if (pn < 1e-6f) pn = 1e-6f; if (pn > 1 - 1e-6f) pn = 1 - 1e-6f;
                bN += -log2f(bit ? pn : 1 - pn);
            }
            x[NCTX + 2] = have ? stretchf(pn) : 0.f;
            float sn = fabsf(x[NCTX + 2]); int conf = sn < 1 ? 0 : sn < 3 ? 1 : sn < 6 ? 2 : 3;
            int set = ((c0 & 1023) + 1024 * (eb < 0 ? 0 : 1 + eb)) * 4 + conf;
            float *wa = wA + set * NIN, *wb = wB + set * NIN; float dA = 0, dB = 0;
            for (int i = 0; i < NIN; i++) { dA += wa[i] * (i == NCTX + 2 ? 0.f : x[i]); dB += wb[i] * x[i]; }
            float pA = squashf(dA), pB = squashf(dB);
            pA = fminf(fmaxf(pA, 1.f / 8192), 1 - 1.f / 8192); pB = fminf(fmaxf(pB, 1.f / 8192), 1 - 1.f / 8192);
            int acx = (c0 & 1023) * 4 + (int)cls1;
            float qA = (pA + 3 * apm_p(&apA, pA, acx)) / 4, qB = (pB + 3 * apm_p(&apB, pB, acx)) / 4;
            qA = fminf(fmaxf(qA, 1.f / 8192), 1 - 1.f / 8192); qB = fminf(fmaxf(qB, 1.f / 8192), 1 - 1.f / 8192);
            bA += -log2f(bit ? qA : 1 - qA); bB += -log2f(bit ? qB : 1 - qB);
            float eA = (bit - pA) * 0.004f, eB = (bit - pB) * 0.004f;
            for (int i = 0; i < NIN; i++) { wa[i] += eA * (i == NCTX + 2 ? 0.f : x[i]); wb[i] += eB * x[i]; }
            apm_up(&apA, bit); apm_up(&apB, bit);
            for (int i = 0; i < NCTX; i++) { Slot *t = s[i]; int tg = bit ? 65535 : 0; t->p += (int)((tg - (int)t->p) * rate[t->n]); if (t->n < 60) t->n++; }
            if (eb >= 0) { int L = mlen < 63 ? mlen : 63; mprob[L] += ((bit == eb) - mprob[L]) * 0.002f; if (bit != eb) expected = -1; }
            c0 = (c0 << 1) | bit;
        }
        if (pos >= nw) { cA[pos - nw] = (float)bA; cB[pos - nw] = (float)bB; totA += bA; totB += bB; totN += bN; }
        if (tok >= 512 && t1 >= 256 && t1 < 512) { w2 = w1; w1 = (t1 - 256) * 256 + (tok - 512) + 1; }
    }
    char fn[1024];
    snprintf(fn, sizeof fn, "%s_cm.f32", argv[4]); FILE *f = fopen(fn, "wb"); fwrite(cA, 4, nt, f); fclose(f);
    snprintf(fn, sizeof fn, "%s_mix.f32", argv[4]); f = fopen(fn, "wb"); fwrite(cB, 4, nt, f); fclose(f);
    printf("{\"test_tokens\": %zu, \"cm_bits\": %.1f, \"mix_bits\": %.1f, \"nn_bits\": %.1f}\n", nt, totA, totB, totN);
    return 0;
}
