"""Patch the actual preserved lexth11c interfaces, checking all anchors first."""
from pathlib import Path
changes={
'src/coder/encoder.cpp':[
 ('#include "encoder.h"\n','#include "encoder.h"\n#include <cmath>\ndouble g_lab_cost_bits=0;\n',1),
 ('  if (bit) {\n    x2_ = xmid;','  g_lab_cost_bits -= std::log2(bit ? p/65536.0 : (65536.0-p)/65536.0);\n  if (bit) {\n    x2_ = xmid;',2)],
'src/runner.cpp':[
 ('int Help() {','extern double g_lab_cost_bits;\nint Help() {',1),
 ('  Encoder e(os, p);','  Encoder e(os, p);\n  FILE* lab_cost=getenv("LAB_COST")?fopen(getenv("LAB_COST"),"wb"):nullptr;',1),
 ('      unsigned char c = static_cast<unsigned char>(buffer[i]);\n      for (int j = 7; j >= 0; --j) {\n        e.Encode((c>>j)&1);\n      }','      unsigned char c = static_cast<unsigned char>(buffer[i]);\n      double lab_before=g_lab_cost_bits;\n      for (int j = 7; j >= 0; --j) {\n        e.Encode((c>>j)&1);\n      }\n      if(lab_cost){float bits=float(g_lab_cost_bits-lab_before);fwrite(&bits,4,1,lab_cost);}',1),
 ('  e.Flush();\n  *output_bytes = os->tellp();','  e.Flush();\n  if(lab_cost)fclose(lab_cost);\n  fprintf(stderr,"\\nLAB ideal cost: %.9f bytes\\n",g_lab_cost_bits/8);\n  *output_bytes = os->tellp();',1),
 ('  } else {\n    preprocessor::NoPreprocess(data_in, temp_out, *input_bytes);\n  }','  } else if(getenv("LAB_RAW")){\n    char buf[1<<20];size_t n;while((n=fread(buf,1,sizeof(buf),data_in)))fwrite(buf,1,n,temp_out);\n  } else {\n    preprocessor::NoPreprocess(data_in, temp_out, *input_bytes);\n  }',1),
 ('  if (temp_bytes < kMinVocabFileSize) {\n    std::fill(vocab.begin(), vocab.end(), true);\n  } else {','  if(getenv("LAB_VOCAB")){\n    FILE* f=fopen(getenv("LAB_VOCAB"),"rb");if(!f)Fail("LAB_VOCAB unreadable");\n    unsigned char bm[32];if(fread(bm,1,32,f)!=32)Fail("LAB_VOCAB short");fclose(f);\n    for(int k=0;k<256;k++)vocab[k]=(bm[k/8]>>(k%8))&1;\n  } else if (temp_bytes < kMinVocabFileSize) {\n    std::fill(vocab.begin(), vocab.end(), true);\n  } else {',1),
 ('    preprocessor::Pretrain(&p, dictionary);\n  }\n  Compress(','    preprocessor::Pretrain(&p, dictionary);\n  } else if(getenv("LAB_DICT")&&!extraction.ppmd_only&&!extraction.transformer_only){\n    FILE* f=fopen(getenv("LAB_DICT"),"rb");if(!f)Fail("LAB_DICT unreadable");preprocessor::Pretrain(&p,f);fclose(f);\n  }\n  Compress(',1),
 ('      remove(".dict");','      if(!getenv("LAB_RAW"))remove(".dict");',1),
 ('  remove(temp_path.c_str());','  if(!getenv("LAB_KEEP_TEMP"))remove(temp_path.c_str());',3)
 ]}
result={}
for name,patches in changes.items():
    text=Path(name).read_text()
    for old,new,count in patches:
        assert text.count(old)==count,(name,count,text.count(old),old)
        text=text.replace(old,new)
    result[name]=text
# No source is written unless every source's anchor count validates.
for name,text in result.items():Path(name).write_text(text)
print('LEX_EXACT_INSTRUMENTATION_APPLIED',flush=True)
