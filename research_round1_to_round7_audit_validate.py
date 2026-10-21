"""Validate and index the evidence audit. No historical experiments are rerun.

Source mappings are a human-authored interpretation of extant sections, not
proof that the underlying proposal was implemented. Fail on missing mappings,
missing files/line anchors, incomplete per-idea answers, or unexpected IDs.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "research_round1_to_round7_idea_audit.md"
MARKER = "\n<!-- audit-coverage-generated -->\n"


def ids(s):
    return [f"A{int(n):02d}" for n in s.split()]


def polish(text):
    """Add missing prose spacing while preserving filenames, URLs and code."""
    parts = re.split(r"(`[^`]+`|\]\([^)]*\))", text)
    words = "about|approximately|roughly|Full|full|Old|old|Round|round|over|across|only|top|Top|all|All|No|no|below|above|after|before|with|at|At|On|on|and|And|not|to|rank|Rank|step|Step|checks|than"
    nouns = "bytes|words|articles|rows|constructors|symbols|bits|targets|queries|families|entries|programs|priors|steps|variants|profiles|factors|examples|calls|streams|tables|records|copies|copy|models|components"
    for i in range(0,len(parts),2):
        s=parts[i]
        s=re.sub(r"(\*\*[123]\.[^*\n]+\*\*)(?=\S)",r"\1 ",s)
        s=re.sub(r"\b("+words+r")(?=\d)",r"\1 ",s)
        s=re.sub(r"(?<=\d)(?=(?:KiB|MiB|GiB|GB|MB|KB|B|s)\b)"," ",s)
        s=re.sub(r"(?<=\d)(?=(?:"+nouns+r")\b)"," ",s)
        parts[i]=s
    return "".join(parts)


# Section line anchors pin the exact source version audited. If a source is
# edited, review its mapping rather than silently interpreting a shifted line.
SECTION_MAP = {
    "hutter_prize_idea1.txt": {
        7:"9", 73:"9 13", 117:"11 12", 166:"11 83", 184:"10 88",
        232:"9", 289:"10", 335:"10", 362:"9 13", 414:"13",
        474:"11 69", 515:"27 71", 566:"27 71", 599:"9 10",
        625:"9 10 11 14 27", 676:"14 90",
    },
    "hutter_prize_idea2.txt": {
        7:"1 2", 51:"4", 107:"6", 164:"6 15 42", 203:"4",
        260:"6 7", 316:"5", 362:"8 29", 410:"6 36 95",
        482:"1 2 3 4 5 6 7 8",
    },
    "idea_arch_1.txt": {
        12:"67", 42:"72", 117:"73", 162:"74", 225:"78",
        307:"79", 359:"78 79 82", 392:"83 84", 451:"83",
        513:"9 13", 553:"6 15", 597:"67", 639:"42 84",
        693:"36 95", 753:"15 64 67", 778:"72 74 78 79 80 83",
    },
    "idea_arch_2.txt": {
        15:"74 77 80", 70:"74 82", 97:"74", 106:"74", 115:"74",
        131:"72", 159:"73", 207:"80", 271:"79 80", 330:"80",
        379:"78 79 82", 445:"80", 495:"68 78 80", 563:"78 81",
        600:"75 80 81", 665:"77 80", 710:"67 82", 783:"79 83",
        835:"80 83", 889:"80 90", 933:"81", 976:"81", 1054:"82",
        1110:"67 78 79 80 83", 1164:"74 75 76 77 78 79 80 81 82 83",
    },
    "hutter_experiments_report.md": {
        1:"16 19 22", 5:"1 2 4 5 8 9 10 11 15 16", 19:"16 93",
        27:"15 16 18 19 22", 29:"16 17", 44:"15 18", 71:"19",
        84:"22", 95:"7 16 17 18 20", 103:"16 19 95", 110:"93",
    },
    "hutter_ideas_report.md": {
        1:"9 10 11 12 24 25 28", 10:"9 10 12 25 28",
        20:"14 36 95", 28:"9 10 11 12 14 24 25 28",
        30:"10", 43:"10 36", 55:"14", 64:"9", 74:"11", 87:"12",
        98:"4 5 6", 107:"19", 114:"15 25 26", 132:"24 25 27 28",
        156:"4 5 9 10 12 24 25 28", 170:"12 24 25 28", 177:"25 28 95",
    },
    "hutter_context_miner_report.md": {
        1:"29 30 31 32 33 34 35 36", 8:"34 35 36", 53:"15 25 29 33",
        83:"19 31 32 33 34 35", 108:"29 30", 132:"36", 146:"33 35 36 95",
    },
    "hutter_round5_report.md": {
        1:"37 38 39 40 41", 7:"37 38 39 40 41", 25:"95", 39:"93 94 95",
        66:"15 36 95", 97:"37 38 39 40 41 42 43 44 45",
        99:"37 38 39 40 41", 109:"20 21 23 42 43 44 45",
        124:"8 15 25 56 72", 156:"93 95", 165:"94",
        172:"37 38 39 40 41 44 56 57 90 95",
    },
    "hutter_round6_report.md": {
        1:"32 46 47 48 49 50 95", 11:"46 47 48 49 50 95",
        48:"32 46 47 48 49 50 56 95", 61:"36 95", 63:"36 95",
        77:"15 47 48 49 54", 99:"15 25 33 71", 108:"32 55",
        128:"46", 155:"47 48 49 50 56", 247:"51 52 53 54 55",
        274:"93 95", 296:"47 49 50 56 90 95", 309:"93 95",
    },
}

# Round-7 registry keys map to consolidated audit families. Historical registry
# statuses are not used as current statuses; corrected final outputs supersede
# earlier provisional root/EOF, graph and launch records.
REGISTRY_MAP = {
    "L01":"17", "L02":"17 40 41", "L03":"17 93", "L04":"93 95",
    "L05":"57", "L06":"58", "L07":"59", "L08":"62", "L09":"63",
    "L10":"42", "L11":"64", "L12":"64", "L13":"65", "L14":"66",
    "L15":"66", "L16":"43", "L17":"45", "L18":"15 76",
    "L19":"68 92 93", "L20":"93", "F01":"93", "I01":"72 73 74 75",
    "I01b":"75", "I01c":"75", "I02":"76", "I03":"77",
    "I03b":"75 77", "I04":"78", "I04b":"71", "I05":"67 79 84",
    "I06":"79", "I07":"24 25 32 71 77", "I08":"73 74",
    "I09":"80 81", "I10":"68 69 70 83 84 90 92", "I11":"85 86 87 88",
    "I11b":"85 86 87", "I11c":"85 87", "I12":"89",
    "P01":"95", "P02":"64", "P03":"63 64 84", "P04":"60 61",
    "P05":"94 95",
}


def main():
    original = REPORT.read_text(encoding="utf-8")
    main_text = polish(original.split(MARKER)[0])
    hits = list(re.finditer(r"^### (A\d{2})\. (.+)$", main_text, re.M))
    expected = [f"A{i:02d}" for i in range(1, 96)]
    assert [h[1] for h in hits] == expected, "Missing, duplicate, or out-of-order audit ID"
    entries = []
    for i, h in enumerate(hits):
        end = hits[i+1].start() if i+1 < len(hits) else main_text.index("\n## What the combination")
        body = main_text[h.end():end].strip()
        body = re.split(r"\n## ", body, maxsplit=1)[0].strip()
        matches = list(re.finditer(r"\*\*([123])\. ([^*]+)\*\*", body))
        assert [m[1] for m in matches] == ["1", "2", "3"], f"Incomplete answers: {h[1]}"
        fields = {}
        for j,m in enumerate(matches):
            fields[m[1]] = body[m.end():matches[j+1].start() if j+1<len(matches) else len(body)].strip()
        entries.append({"id":h[1], "title":h[2],
                        "report_line":main_text[:h.start()].count("\n")+1,
                        "rigor_applied":fields["1"], "actual_testing_and_needed_testing":fields["2"],
                        "combination_work":fields["3"], "thinking_hours":"NOT_RECORDED_OR_VERIFIABLE"})

    coverage=[]
    for name,mapping in SECTION_MAP.items():
        p=ROOT/name
        lines=p.read_text(encoding="utf-8-sig").splitlines()
        observed={i+1:line for i,line in enumerate(lines) if re.match(r"^#{1,6} ",line)}
        assert set(observed)==set(mapping), f"Review source-section mapping: {name}, missing={set(observed)-set(mapping)}, obsolete={set(mapping)-set(observed)}"
        for line,heading in observed.items():
            targets=ids(mapping[line])
            assert set(targets)<=set(expected)
            coverage.append({"file":name,"line":line,"heading":heading.lstrip("# "),"audit_ids":targets,
                             "mapping_type":"SOURCE_SECTION_TO_RECOVERABLE_FAMILY"})

    # Every L-row and every explicitly registered I/F/P item in the original
    # pre-experiment report must have a coverage key. This is a coverage check,
    # not a claim that every registration was completed.
    registry_file="research_round7_pre_experiment_report.md"
    reg_text=(ROOT/registry_file).read_text(encoding="utf-8-sig")
    found=set(re.findall(r"\b(?:L\d{2}|[IF]\d{2}[bc]?|P\d{2})\b",reg_text))
    assert found<=set(REGISTRY_MAP), f"Unmapped registered experiments: {found-set(REGISTRY_MAP)}"
    registry=[]
    for key,target in REGISTRY_MAP.items():
        refs=[]
        for name in (registry_file,"research_round7_remaining_experiments_report.md"):
            for i,line in enumerate((ROOT/name).read_text(encoding="utf-8-sig").splitlines(),1):
                if re.search(r"\b"+re.escape(key)+r"\b",line):
                    refs.append({"file":name,"line":i})
        registry.append({"key":key,"audit_ids":ids(target),"references":refs,
                         "note":"Historical registration; consult corrected final evidence for current status."})

    # Verify all explicit local evidence links and collect source hashes.
    refs=re.findall(r"\]\((/C:/[^)]+)\)",main_text)
    sources={}
    for target in refs:
        pathline=target[1:]
        if re.search(r":\d+$",pathline):
            name,ln=pathline.rsplit(":",1)
            line=int(ln)
        else:name,line=pathline,None
        p=Path(name)
        assert p.is_file(),f"Missing evidence link: {target}"
        assert p.resolve().is_relative_to(ROOT.resolve()),f"Unexpected source outside workspace: {target}"
        if line:
            assert line<=len(p.read_text(encoding="utf-8-sig").splitlines()),f"Bad line anchor: {target}"
        rel=p.relative_to(ROOT).as_posix()
        sources[rel]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    for name in SECTION_MAP:
        p=ROOT/name
        sources[name]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

    appendix=[MARKER, "## Coverage appendix: extant proposal and report sections", "",
              "This mapping is exhaustive for the headings in the four surviving idea files and rounds2–6 reports. The round2 earlier-lab section is the recoverable round1 source. A heading can cover several variants and maps to multiple consolidated families. It does not assert all those families were implemented.", "",
              "| Source section (line) | Audit families |", "|---|---|"]
    for c in coverage:
        path="/C:/Users/91707/Downloads/compression_cmix/"+c["file"]+":"+str(c["line"])
        label=c["file"]+":"+str(c["line"])+" — "+c["heading"].replace("|","\\|")
        appendix.append(f"| [{label}]({path}) | {', '.join(c['audit_ids'])} |")
    appendix += ["", "### Round7 experiment-registry coverage", "",
                 "Registry names are retained for handoff. The report's dated provisional statuses are superseded where later corrected evidence exists. Coverage is not a completion flag.", "",
                 "| Registry item | Audit families |", "|---|---|"]
    for r in registry:appendix.append(f"| {r['key']} | {', '.join(r['audit_ids'])} |")
    appendix += ["", "Validation checks 95 ordered entries, three answers for every entry, all mapped source headings, registered experiment IDs, existing evidence files and valid file-line anchors. The accompanying JSON includes source SHA256 hashes, per-entry fields and exact mappings. It validates the report's structure/provenance; it does not reproduce historical experiments.", ""]
    final=main_text+"\n".join(appendix)
    REPORT.write_text(final,encoding="utf-8")
    manifest={"date_local":"2026-10-06","timezone":"Asia/Calcutta",
              "status":"AUDIT_COMPLETE_FOR_RECOVERABLE_SOURCES",
              "audit_entries":entries,"source_section_coverage":coverage,
              "round7_registry_coverage":registry,"sources":sources,
              "missing_evidence":["standalone round1 eighteen-idea ledger and raw run identities",
                                  "original expert_advice.txt referenced by round6",
                                  "original round6/ directory (selected sources survive under research_round7_sources)",
                                  "per-idea private thinking-hour records"],
              "report_sha256":hashlib.sha256(final.encode()).hexdigest(),
              "new_experiments_run":False,"paid_rental_spend_usd":0,"files_deleted":[],
              "structure_validation":{"ordered_entries":len(entries),"answer_fields":len(entries)*3,
                                      "mapped_source_sections":len(coverage),"registry_keys":len(registry),
                                      "linked_source_files":len(sources)},
              "claim_limit":"Coverage of recoverable sources, not proof of complete history, optimality, or qualifying improvement."}
    (ROOT/"research_round1_to_round7_idea_audit.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"PASS",**manifest["structure_validation"],"report_bytes":REPORT.stat().st_size,
                      "report_words":len(final.split()),"report_sha256":manifest["report_sha256"]}))


if __name__=="__main__":main()
