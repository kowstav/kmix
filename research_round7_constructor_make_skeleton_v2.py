"""Generate V2 without changing the already measured V1 sources/results."""
import pathlib
root=pathlib.Path(__file__).parent
p=root/'research_round7_constructor_skeleton.py';src=p.read_text(encoding='utf-8')
changes=[
 ('I11b fixed skeleton layout','I11c fixed one-byte-marker skeleton layout'),
 ('Raw zero is escaped as 00 00; a removed constructor span becomes 00 01.',
  'Raw zero is escaped as 00 00 and raw08 as00 08; removed constructors become08.'),
 ("DEST=ROOT/'constructor_skeleton_v1'","DEST=ROOT/'constructor_skeleton_v2'"),
 ("skeleton.extend(raw[pos:a].replace(b'\\x00',b'\\x00\\x00'));skeleton.extend(b'\\x00\\x01')",
  "skeleton.extend(raw[pos:a].replace(b'\\x00',b'\\x00\\x00').replace(b'\\x08',b'\\x00\\x08'));skeleton.append(8)"),
 ("skeleton.extend(raw[pos:].replace(b'\\x00',b'\\x00\\x00'))",
  "skeleton.extend(raw[pos:].replace(b'\\x00',b'\\x00\\x00').replace(b'\\x08',b'\\x00\\x08'))"),
 ("        if c:out.append(c);continue\n        assert i<len(skeleton);flag=skeleton[i];i+=1\n        if flag==0:out.append(0)\n        else:\n            assert flag==1 and j<len(words);out.extend(words[j]);j+=1",
  "        if c==0:\n            assert i<len(skeleton);literal=skeleton[i];i+=1\n            assert literal in (0,8);out.append(literal)\n        elif c==8:\n            assert j<len(words);out.extend(words[j]);j+=1\n        else:out.append(c)"),
 ("b'CSP1'","b'CSP2'"),
 ("def selftest():\n", "def selftest():\n    for x in range(256):\n        raw=bytes([x])+b'aa'+bytes([x])+b'aa'+bytes([x])\n        for mode in (0,1):\n            c,g,_=transform(raw,[(1,3),(4,6)],mode);assert inverse(c,g)==raw\n"),
 ('I11b_marker_escape_boundary_EOF_roundtrip','I11c_one_byte_marker_256_literal_boundaries_roundtrip'),
 ('I11b constructor skeleton insertion layout','I11c one-byte constructor marker layout'),
 ('zero escape and insertion markers','fixed08 one-byte marker with00 escape of raw00/08')]
for old,new in changes:
    assert src.count(old)>=1,old
    if old!="b'CSP1'":assert src.count(old)==1,(old,src.count(old))
    src=src.replace(old,new)
(root/'research_round7_constructor_skeleton_v2.py').write_text(src,encoding='utf-8')
print('V2 source generated; V1 unchanged')
