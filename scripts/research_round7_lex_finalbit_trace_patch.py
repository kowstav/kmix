"""Checked, observation-only trace patch on isolated original lex sources.

LAB_BITTRACE stores little-endian uint16 FINAL p(bit=1) in Encode(), before
Perceive(). No neural probabilities, raw-bit calls or training observations.
The native arithmetic calculation and all predictors remain unchanged.
"""
import argparse
import ast
import hashlib
import json
import pathlib

TRACE_INCLUDE = '''#include <cstdio>
#include <cstdlib>
static FILE* hp_final_bit_trace = nullptr;
'''
TRACE_WRITE = '''  if (const char* trace_path = std::getenv("LAB_BITTRACE")) {
    if (!hp_final_bit_trace) hp_final_bit_trace = std::fopen(trace_path, "wbx");
    if (!hp_final_bit_trace) std::abort();
    const unsigned char little_endian_p[2] = {
        static_cast<unsigned char>(p & 255),
        static_cast<unsigned char>((p >> 8) & 255)};
    if (std::fwrite(little_endian_p, 1, 2, hp_final_bit_trace) != 2) std::abort();
  }
'''
TRACE_CLOSE = '''  if (hp_final_bit_trace) {
    if (std::fclose(hp_final_bit_trace) != 0) std::abort();
    hp_final_bit_trace = nullptr;
  }
'''


def exact_lab_changes(path):
    # Read the existing validated patch as data; never execute its global writes.
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and
                any(isinstance(t, ast.Name) and t.id == 'changes' for t in n.targets))
    return ast.literal_eval(node.value)


def patch_texts(original, lab_changes):
    result = dict(original)
    for name, changes in lab_changes.items():
        text = result[name]
        for old, new, count in changes:
            if text.count(old) != count:
                raise ValueError(('Lab patch anchor drift', name, count, text.count(old)))
            text = text.replace(old, new)
        result[name] = text
    p = 'src/runner.cpp'
    text = result[p]
    changes = [(
        '      preprocessor::Pretrain(&p, dictionary);\n    }\n\n    std::ofstream temp_out',
        '      preprocessor::Pretrain(&p, dictionary);\n    } else if(getenv("LAB_DICT")&&!extraction.ppmd_only&&!extraction.transformer_only){\n      FILE* f=fopen(getenv("LAB_DICT"),"rb");if(!f)Fail("LAB_DICT unreadable");preprocessor::Pretrain(&p,f);fclose(f);\n    }\n\n    std::ofstream temp_out'), (
        '\n  preprocessor::Decode(temp_in, data_out, dictionary);',
        '\n  if(getenv("LAB_RAW")){\n    char buf[1<<20];size_t n;while((n=fread(buf,1,sizeof(buf),temp_in)))fwrite(buf,1,n,data_out);\n  } else preprocessor::Decode(temp_in, data_out, dictionary);')]
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError(('Roundtrip patch anchor drift', old))
        text = text.replace(old, new)
    result[p] = text
    p = 'src/coder/encoder.cpp'
    text = result[p]
    anchor = '  const unsigned int p = Discretize(p_->Predict());\n'
    if text.count(anchor) != 1 or text.count('void Encoder::Flush() {\n') != 1:
        raise ValueError('Final coder trace anchor drift')
    text = text.replace('#include <cmath>\n', '#include <cmath>\n' + TRACE_INCLUDE)
    text = text.replace(anchor, anchor + TRACE_WRITE)
    text = text.replace('void Encoder::Flush() {\n', 'void Encoder::Flush() {\n' + TRACE_CLOSE)
    # Trace is confined to the actual coded bit and final Flush. Raw/observe
    # method bodies remain exactly identical to the matched lab instrument.
    before = result[p].split('void Encoder::EncodeRawBit', 1)[1].split('void Encoder::Flush()', 1)[0]
    after = text.split('void Encoder::EncodeRawBit', 1)[1].split('void Encoder::Flush()', 1)[0]
    assert before == after
    result[p] = text
    return result


def tests(root):
    sources = root / 'research_round7_sources'
    originals = {'src/coder/encoder.cpp': (sources / 'lex_encoder.cpp').read_text(),
                 'src/runner.cpp': (sources / 'lex_runner.cpp').read_text()}
    patched = patch_texts(originals, exact_lab_changes(root / 'research_round7_lex_exact_labpatch.py'))
    assert 'const unsigned int p = Discretize(p_->Predict());\n' + TRACE_WRITE in patched['src/coder/encoder.cpp']
    assert patched['src/coder/encoder.cpp'].count('std::fwrite(little_endian_p') == 1
    # A source with changed interfaces must fail before any file write.
    changed = dict(originals)
    changed['src/coder/encoder.cpp'] = changed['src/coder/encoder.cpp'].replace('Discretize(p_->Predict())', 'Discretize(p_->PredictChanged())')
    try:
        patch_texts(changed, exact_lab_changes(root / 'research_round7_lex_exact_labpatch.py'))
    except ValueError:
        pass
    else:
        raise AssertionError('Anchor drift accepted')
    return {'self_tests': 'PASS', 'checked': ['all original lex lab anchors', 'both roundtrip anchors',
            'trace before Perceive', 'exclusive little-endian trace output',
            'raw and observation methods unchanged', 'drift fails before writes'],
            'patched_source_sha256': {n: hashlib.sha256(s.encode()).hexdigest() for n, s in patched.items()},
            'scope': 'Source transformation validation; native compile/trace parity/decode not yet run'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--tree')
    ap.add_argument('--lab-patch')
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(tests(pathlib.Path(__file__).parent), indent=2))
        return
    tree, source = pathlib.Path(args.tree), pathlib.Path(args.lab_patch)
    originals = {n: (tree / n).read_text() for n in ('src/coder/encoder.cpp', 'src/runner.cpp')}
    patched = patch_texts(originals, exact_lab_changes(source))
    # All checks complete before mutation. This tree must be an isolated copy.
    for n, text in patched.items():
        (tree / n).write_text(text)
    print('LEX_FINALBIT_TRACE_PATCH_APPLIED', flush=True)


if __name__ == '__main__':
    main()
