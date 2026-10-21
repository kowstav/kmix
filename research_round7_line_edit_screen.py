"""Prefix-keyed near-repeat lines, with charged copy/edit marginal likelihoods.

General main-text probe beyond infoboxes. The first four original coded bytes
are paid to the baseline. The decoder then selects past completed lines using
that observed prefix (optionally masking observed digits), before seeing the
continuation. Target-informed donor/alignment choice is never used.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
import research_round7_field_screen as F
from research_round7_edit_screen import EditScore
from research_round7_wrt import inverse_byte,load_dictionary


def screen(raw,costs,dictionary,mask_digits=False,edit=True):
    if len(raw)!=len(costs):raise ValueError('Incomplete byte costs')
    offset=raw.find(F.literal_wrt(F.SEP,dictionary))
    if offset<0:raise ValueError('No synchronization separator')
    scores=F.Scores(raw,costs,F.DEFAULT_PRIORS,512)
    typ=EditScore if edit else F.Score
    scores.scores={'line_copy':typ('line_copy',F.DEFAULT_PRIORS,scores.prefix_cost[-1]),
                   'combined':typ('combined',F.DEFAULT_PRIORS,scores.prefix_cost[-1])}
    memory=F.ValueMemory(max_keys=65536,max_bytes=16<<20,donors=2)
    events=completed=lines=0
    pos=offset
    while pos<len(raw):
        # Equivalent to consuming bytes until newline; end is an OBSERVED
        # stopping boundary, not a feature supplied to candidate selection.
        end=raw.find(b'\n',pos)
        closed=end>=0
        end=end+1 if closed else len(raw)
        if end<=pos:raise RuntimeError('Nonadvancing line parser')
        prefix=raw[pos:min(pos+4,len(raw))]
        start=pos+4
        if len(prefix)==4 and b'\n' not in prefix:
            key=bytes(63 if 48<=c<=57 else c for c in prefix) if mask_digits else prefix
            donors=memory.get((key,b'line'))
            candidates=[F.Candidate(line[4:],.5**j,available) for j,(line,available) in enumerate(donors)]
            first=inverse_byte(prefix[0])
            kind='table_list' if first in (33,35,42,58,59,123,124,125) else 'indent' if first in (9,32) else 'prose'
            context=(kind,min(len(donors),2))
            ev=scores.begin('line_copy',start,candidates,context)
            if ev:
                events+=1
                if closed or end>=ev.cap:scores.finish(ev,min(end,ev.cap),'line_stop' if closed else 'cap')
            if closed:
                # Eligibility is determined only after this complete source is
                # decoded, for future events. Long donors are not truncated.
                source=raw[pos:end]
                if 4<len(source)<=512:
                    memory.add((key,b'line'),source,end);completed+=1
        scores.advance(end)
        lines+=1;pos=end
    scores.eof()
    r=scores.scores['combined'].result()
    return {'raw_bytes':len(raw),'baseline_ideal_bytes':float(scores.prefix_cost[-1]/8.),
            'mask_observed_prefix_digits':mask_digits,'edit_channel':edit,
            'contract':'first four bytes paid; only past completed donors; target end is decoded stop; oracle diagnostic is unpaid',
            'lines':lines,'completed_stored_sources':completed,'proposed_events':events,
            'memory_keys':len(memory.data),'accounted_memory_payload_bytes':memory.bytes,
            'score':r}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--slice',required=True);ap.add_argument('--cost',required=True);ap.add_argument('--dictionary',required=True);ap.add_argument('--out',required=True);ap.add_argument('--mask-digits',action='store_true');ap.add_argument('--exact',action='store_true');args=ap.parse_args()
    report=screen(Path(args.slice).read_bytes(),np.fromfile(args.cost,'<f4'),load_dictionary(args.dictionary),args.mask_digits,not args.exact)
    Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['raw_bytes','baseline_ideal_bytes','mask_observed_prefix_digits','edit_channel','lines','proposed_events','memory_keys']}|{'score':{k:report['score'][k] for k in ['prequential_saving_bytes','baseline_bits_covered','coded_bytes_covered']}}),flush=True)
