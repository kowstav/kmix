# Final transformer-aware blend after the SSE stage (lab, env-gated: LAB_FINALMIX=<lr>).
# p_out = sigmoid( w . [st(p_sse), st(p_mix1), st(p_tf), 1] ), weight set selected by
# (bit position 0..7) x (transformer confidence bucket 0..11); init w = [1,0,0,0] (= baseline).
def patch(path, old, new, count=1):
    s = open(path, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))

P = 'src/predictor.cpp'
patch(P, '''int lstmpr=0, lstmex=0;
float byte_mixer_output=0.0f;''', '''int lstmpr=0, lstmex=0;
float byte_mixer_output=0.0f;
namespace {
struct FinalMix {
  float lr = 0.0f;
  float w[8 * 12][4];
  float x[4];
  int sel = 0;
  float p = 0.5f;
  int bitpos = 0;
  FinalMix() {
    const char* e = getenv("LAB_FINALMIX");
    if (e) lr = (float)atof(e);
    for (int i = 0; i < 8 * 12; ++i) { w[i][0] = 1.0f; w[i][1] = w[i][2] = w[i][3] = 0.0f; }
  }
  static float st(float q) {
    if (q < 1e-6f) q = 1e-6f;
    if (q > 1.0f - 1e-6f) q = 1.0f - 1e-6f;
    return logf(q / (1.0f - q));
  }
  float Mix(float p_sse, float p_mix, float p_tf) {
    x[0] = st(p_sse); x[1] = st(p_mix); x[2] = st(p_tf); x[3] = 0.25f;
    float conf = fabsf(x[2]);
    int cb = conf < 0.5f ? 0 : conf < 1.0f ? 1 : conf < 1.5f ? 2 : conf < 2.0f ? 3 :
             conf < 3.0f ? 4 : conf < 4.0f ? 5 : conf < 5.0f ? 6 : conf < 6.0f ? 7 :
             conf < 7.0f ? 8 : conf < 8.0f ? 9 : conf < 10.0f ? 10 : 11;
    sel = bitpos * 12 + cb;
    float d = 0.0f;
    for (int i = 0; i < 4; ++i) d += w[sel][i] * x[i];
    if (d > 20.0f) d = 20.0f;
    if (d < -20.0f) d = -20.0f;
    p = 1.0f / (1.0f + expf(-d));
    return p;
  }
  void Update(int bit) {
    float err = (float)bit - p;
    for (int i = 0; i < 4; ++i) w[sel][i] += lr * err * x[i];
    bitpos = (bitpos + 1) & 7;
  }
} g_finalmix;
}  // namespace''')
patch(P, '''  float p = Sigmoid::Logistic(mixer_1_[0].Mix());
  p = sse_.Predict(p);
  if (byte_mixer_override >= 0) {
    return byte_mixer_override;
  }
  return p;''', '''  float p = Sigmoid::Logistic(mixer_1_[0].Mix());
  float p_mix = p;
  p = sse_.Predict(p);
  if (g_finalmix.lr > 0.0f) {
    p = g_finalmix.Mix(p, p_mix, byte_mixer_output);
    if (p < 1.0f / 32768) p = 1.0f / 32768;
    if (p > 1.0f - 1.0f / 32768) p = 1.0f - 1.0f / 32768;
  }
  if (byte_mixer_override >= 0) {
    return byte_mixer_override;
  }
  return p;''')
patch(P, '''  sse_.Perceive(bit);

  bool byte_update = false;''', '''  sse_.Perceive(bit);
  if (g_finalmix.lr > 0.0f) g_finalmix.Update(bit);

  bool byte_update = false;''')
print('final-mix patch applied')
