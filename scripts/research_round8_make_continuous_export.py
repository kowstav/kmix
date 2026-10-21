
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
R=project_root(__file__)
base=(project_path('research_round8_semantic_replay.cpp', base=R)).read_text(encoding='utf-8')
base=base.replace('void run_clean8(string rp,string pp,string dict,string graph,string cons,string semantic,size_t limit,string out)', 'void run_clean8(string rp,string pp,string dict,string graph,string cons,string semantic,size_t limit,string out)')
base=base.replace('array<Gate8,6>gates;int node=0;', 'ofstream features(out+".features",ios::binary);uint64_t exported_bits=0;int node=0;')
begin=base.index('   array<pair<double,double>,6>sig=')
end=base.index('if(node>=0)node=x.tr[node].c[y];',begin)
base=base[:begin]+r'''   uint16_t pp=p;uint8_t yy=y;features.write(reinterpret_cast<char*>(&pp),2);features.write(reinterpret_cast<char*>(&yy),1);for(int k:{0,1,4,10,11,8}){float v=prose?d[k]:0;features.write(reinterpret_cast<char*>(&v),4);}exported_bits++;double base=(y?p:65536-p)/65536.;atomcost-=log2(base);
   '''+base[end:]
begin=base.index(' for(int a=0;a<6;a++){auto&g=gates[a];')
end=base.index('\n}',begin)
base=base[:begin]+r''' if(exported_bits!=8*(raw.size()-offset))throw runtime_error("export bit accounting");features.close();f<<"],\"exported_bits\":"<<exported_bits<<",\"record_bytes\":27,\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"status\":\"CONTINUOUS_FEATURE_EXPORT_NOT_ARCHIVE\",\"core_training\":false,\"deletions\":[]}";'''+base[end:]
(project_path('research_round8_continuous_export.cpp', base=R)).write_text(base,encoding='utf-8')
