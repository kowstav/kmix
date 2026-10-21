"""Fixed topic-pseudocount comparison; normalized, prefix-derived, no neural SGD.

Changes only topic prior strength relative to the preserved v2 family. Queue
behind the already-running v2 screen and native recovery; do not duplicate it.
"""
import pathlib,json,time,traceback,numpy as np
import research_round7_causal_latent_word_v2_screen as previous
import research_round7_word_root_causal_v2 as root
from research_round7_wrt import load_dictionary

SCALE=previous.SCALE
class FixedTopic(previous.Topic):
    def components(self,w,global_count):
        # pi_z sums to one across words, even as the global prefix grows.
        pi=(global_count+self.kappa*self.rank[w])*self.h[w]/(self.global_h+self.kappa*self.initial)
        theta=(self.c[w]+SCALE*64*pi)/(self.total+SCALE*64)
        phi=(self.doc+SCALE*.25)/(self.doc.sum()+self.k*SCALE*.25)
        return phi*theta

class FixedWords(previous.CausalLatentWords):
    last_instance=None
    def __init__(self,codes,spellings):
        super().__init__(codes,spellings)
        self.topics=[FixedTopic(spellings,self.rank,8,0),FixedTopic(spellings,self.rank,8,128),
                     FixedTopic(spellings,self.rank,16,0),FixedTopic(spellings,self.rank,16,256)]
        self.family_names=['rank_prior','global_rank64','topic8_fixed64_article',
                           'topic8_fixed64_decay128','topic16_fixed64_article','topic16_fixed64_decay256']
        FixedWords.last_instance=self

def tests():
    codes=[bytes([128+i]) for i in range(6)];spellings=[b'apple',b'pear',b'fruit',b'king',b'crown',b'queen']
    old=previous.CausalLatentWords(codes,spellings);new=FixedWords(codes,spellings)
    assert np.allclose([old.predictions(w) for w in range(6)],[new.predictions(w) for w in range(6)],atol=1e-14,rtol=0)
    error=0.
    for j in range(320):
        if j%16==0:new.reset()
        total=sum(new.predictions(w) for w in range(6));error=max(error,float(np.max(np.abs(total-1))))
        assert np.allclose(total,1,atol=1e-12,rtol=0),'Fixed topic prior is not normalized'
        new.update([0,2,1,2,4,3,5,3][j%8])
        for t in new.topics:assert np.array_equal(t.c.sum(axis=0),t.total)
    root.Words=FixedWords;root.self_test()
    print(json.dumps({'normalization_max_error':error,'initial_predictions_equal_v2':True,
                     'integer_responsibility_mass':SCALE,'root_literal_case_escape_accounting':'passed'}),flush=True)

if __name__=='__main__':
    tests();out=pathlib.Path('/kaggle/working/hp_round7');dest=out/'causal_latent_words_v3'
    dest.mkdir(exist_ok=False)
    print('WAITING_FOR_EXISTING_V2_AND_NATIVE_RECOVERY',flush=True)
    for _ in range(2880):
        a=(out/'causal_latent_v2_controller.log').read_text();b=(out/'lex_native_2m_recovery_controller.log').read_text()
        if 'Traceback' in a or 'Traceback' in b:raise RuntimeError('An existing prerequisite job failed; inspect evidence')
        if 'CAUSAL_LATENT_WORDS_COMPLETE' in a and 'LEX_NATIVE_2M_RECOVERY_COMPLETE' in b:break
        time.sleep(5)
    else:raise RuntimeError('Four-hour bounded prerequisite wait expired')
    dictionary=load_dictionary(out/'preserved/gen/.dict');rows=[]
    # Same fixed family, alpha grid, contexts, root charges and cold slices.
    for n in 'bc':
        inp=out/'preserved/slices/b2m.bin' if n=='b' else out/'c2m.bin'
        raw=inp.read_bytes();cost=np.fromfile(out/'lex_native_2m'/(n+'_cost.f32'),'<f4')
        assert len(raw)==len(cost)==2000000
        root.Words=FixedWords;r=root.screen(raw,cost,dictionary);model=FixedWords.last_instance
        r['contract'].update(families=model.family_names,prior='Per-topic fixed64 decoded-word-equivalent pseudocount; its normalized rank/global/hash distribution uses only prefix counts',
            change_from_v2='Topic prior strength no longer grows in proportion to all global word occurrences',
            baseline='Actual lexical checkpoint cold2M final native costs',all_root_choices_charged=True,
            decay='127/128 or255/256 per completed dictionary atom; exponential, not hard expiry',
            neural_training=False,paid_rental_usd=0,deletions=[])
        r['prototype_array_bytes']=model.memory_bytes()
        r['topic_learned_mass_fractions']=[{'family':name,'fractions':(t.total/(t.total+SCALE*64)).tolist()} for name,t in zip(model.family_names[2:],model.topics)]
        (dest/(n+'.json')).write_text(json.dumps(r,indent=2))
        rows.append({'slice':n,'saving_bytes_before_native_code_cost':r['score']['prequential_saving_bytes'],
                     'wall_seconds':r['wall_seconds']})
        (dest/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
    print('CAUSAL_LATENT_WORDS_V3_COMPLETE',flush=True)
