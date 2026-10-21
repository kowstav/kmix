from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'research_round8_clean_title_v4.cpp').read_text(encoding='utf-8').splitlines()
assert s[-1].startswith('int main(')
(R/'research_round8_clean_title_library.h').write_text('\n'.join(s[:-1])+'\n',encoding='utf-8')
