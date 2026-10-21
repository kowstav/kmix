import pathlib,json
root=pathlib.Path(__file__).parent
rows=[]
for name in 'abcd':
    row={'slice':name}
    for mode in ['balanced','edit']:
        p=root/f'research_round7_{name}_corrected_{mode}_screen.json'
        if p.exists():row[mode]=json.loads(p.read_text())['scores']['combined']['prequential_saving_bytes']
    for mode in ['exact','edit','masked_edit']:
        p=root/f'research_round7_{name}_line_{mode}.json'
        if p.exists():row['line_'+mode]=json.loads(p.read_text())['score']['prequential_saving_bytes']
    for tag in ['word_context_atlas','calibration_screen']:
        p=root/f'research_round7_{name}_{tag}.json'
        if p.exists():row[tag]=json.loads(p.read_text())
    rows.append(row)
(root/'research_round7_summary.json').write_text(json.dumps(rows,indent=2))
for row in rows:print({k:round(v,9) if isinstance(v,float) else v for k,v in row.items() if k not in ['word_context_atlas','calibration_screen']})
for tag in ['word_context_atlas','calibration_screen']:
    p=root/('research_round7_b_'+tag+'.json')
    if p.exists():print(tag,p.read_text()[:4500])
