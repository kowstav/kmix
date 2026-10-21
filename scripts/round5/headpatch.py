# Online output-head adaptation ("OHA") for the fx2-cmix transformer.
# logits += dW . x + db  (x = dequantized int8 input of the unembedding), and after each coded
# token: SGD step on dW, db with the true token (carried across articles, never reset).
# LR from env FX2_OHA_LR (default 0 = disabled) so A/B lab runs use one binary.
def patch(path, old, new, count=1):
    s = open(path, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)

H = 'cpp_infer/src/opt/model_opt.h'
C = 'cpp_infer/src/opt/model_opt.cpp'
patch(H, '''  // the 205 post-softcap logits of the last step (valid until the next step)
  const float* last_logits() const;''',
'''  // the 205 post-softcap logits of the last step (valid until the next step)
  const float* last_logits() const;

  // Online head adaptation: after the true next token is known, call
  // adapt(token) once (before the next step) to update the head delta.
  // No-op unless enabled (set_head_lr > 0) and the last step predicted it.
  void set_head_lr(float lr);
  void adapt(uint8_t next_token);''')

patch(C, '''  alignas(64) float logits[208] = {};
  alignas(64) float probs208[208] = {};''',
'''  alignas(64) float logits[208] = {};
  alignas(64) float probs208[208] = {};
  // ---- online head adaptation (OHA) state ----
  float oha_lr = 0.0f;
  bool oha_valid = false;
  alignas(64) float oha_x[192] = {};
  alignas(64) float oha_db[208] = {};
  alignas(64) float oha_dW[205 * 192] = {};''')

patch(C, '''      qgemv_f32(M.unembed.m, q5, logits);  // rows_padded 208
    }''',
'''      qgemv_f32(M.unembed.m, q5, logits);  // rows_padded 208
    }
    if (oha_lr > 0.0f) {
      const float s = M.unembed.s_act;
      for (int i = 0; i < D; i++) oha_x[i] = (float)((int)q5[i] - 128) * s;
      for (int o = 0; o < V; o++) {
        const float* w = oha_dW + o * D;
        float a = 0.0f;
        for (int i = 0; i < D; i++) a += w[i] * oha_x[i];
        logits[o] += a + oha_db[o];
      }
    }''')

patch(C, '''      head_softcap_softmax(logits, probs208);
      std::memcpy(probs_out, probs208, sizeof(float) * V);
    }
    t++;
  }''',
'''      head_softcap_softmax(logits, probs208);
      std::memcpy(probs_out, probs208, sizeof(float) * V);
    }
    oha_valid = oha_lr > 0.0f;
    t++;
  }

  void oha_adapt(int y) {
    if (!oha_valid) return;
    oha_valid = false;
    for (int o = 0; o < V; o++) {
      const float th = logits[o] / 15.0f;  // logits now hold 15*tanh(l/15)
      const float g = (probs208[o] - (o == y ? 1.0f : 0.0f)) * (1.0f - th * th);
      const float c = oha_lr * g;
      float* w = oha_dW + o * D;
      for (int i = 0; i < D; i++) w[i] -= c * oha_x[i];
      oha_db[o] -= c;
    }
  }''')

patch(C, '''const float* TransformerOpt::last_logits() const { return impl->logits; }''',
'''const float* TransformerOpt::last_logits() const { return impl->logits; }

void TransformerOpt::set_head_lr(float lr) { impl->oha_lr = lr; }

void TransformerOpt::adapt(uint8_t next_token) { impl->oha_adapt(next_token); }''')

# predictor: enable from env and call adapt with each completed token
P = 'src/predictor.cpp'
patch(P, '''    transformer_.reset(new fx2::opt::TransformerOpt(
        options.transformer_weights.c_str(), fx2::opt::AttnKind::KVI8));''',
'''    transformer_.reset(new fx2::opt::TransformerOpt(
        options.transformer_weights.c_str(), fx2::opt::AttnKind::KVI8));
    if (getenv("FX2_OHA_LR")) transformer_->set_head_lr(atof(getenv("FX2_OHA_LR")));''')
patch(P, '''  memmove(separator_window_, separator_window_ + 1,
      sizeof(separator_window_) - 1);''',
'''  // the completed byte is the target of the transformer's last prediction
  transformer_->adapt((uint8_t)token);
  memmove(separator_window_, separator_window_ + 1,
      sizeof(separator_window_) - 1);''')
print('head-adaptation patch applied')
