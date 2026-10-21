from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'research_round8_conditional.cpp').read_text(encoding='utf-8')
lines=s.splitlines()
assert lines[-1].startswith('int main(')
(R/'research_round8_conditional_library.h').write_text('\n'.join(lines[:-1])+'\n',encoding='utf-8')
