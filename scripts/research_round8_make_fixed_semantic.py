
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
s=(project_path('research_round8_semantic_replay.cpp', base=R)).read_text(encoding='utf-8')
s=s.replace('size_t limit,string out){\n auto start=', 'size_t limit,string out,string coefficient_file){\n auto start=')
s=s.replace('array<Gate8,6>gates;int node=0;', r'''ifstream coefficients(coefficient_file);array<vector<double>,6>theta;for(int a=0;a<6;a++){int n;coefficients>>n;if(n!=(a?4:2))throw runtime_error("coefficient shape");theta[a].resize(n);for(double&v:theta[a])coefficients>>v;}if(!coefficients)throw runtime_error("coefficient file");array<double,6>gain{};array<uint64_t,6>hash;hash.fill(1469598103934665603ULL);array<ofstream,6>qfiles;if(limit)for(int a=0;a<6;a++)qfiles[a].open(out+".q"+to_string(a),ios::binary);vector<double>marginal(x.w.size(),0);double off_gain=0;uint64_t bits=0;int node=0;''')
begin=s.index('   array<pair<double,double>,6>sig=');end=s.index('if(node>=0)node=x.tr[node].c[y];',begin)
s=s[:begin]+r'''   array<double,6>v;int ki=0;for(int k:{0,1,4,10,11,8})v[ki++]=double(float(prose?d[k]:0));double base=(y?p:65536-p)/65536.;atomcost-=log2(base);
   for(int a=0;a<6;a++){auto&t=theta[a];double z=l+t[0]+t[1]*l;if(a)z+=t[2]*v[a-1]+t[3]*v[5];int q=quant(1./(1.+exp(-z)));double likelihood=(y?q:65536-q)/65536.;gain[a]+=log2(likelihood/base);hash[a]^=uint64_t(q);hash[a]*=1099511628211ULL;if(limit){uint16_t qq=q;qfiles[a].write(reinterpret_cast<char*>(&qq),2);}if(a==1){double zoff=l+t[0]+t[1]*l+t[3]*v[5];int qo=quant(1./(1.+exp(-zoff)));double po=(y?qo:65536-qo)/65536.;off_gain+=log2(po/base);if(x.lastcontent>=0)marginal[x.lastcontent]+=log2(likelihood/po)/8.;else if(q!=qo)throw runtime_error("unavailable semantic source changed prediction");}}
   bits++;'''+s[end:]
begin=s.index(' for(int a=0;a<6;a++){auto&g=gates[a];');end=s.index('\n}',begin)
s=s[:begin]+r''' if(bits!=8*(raw.size()-offset))throw runtime_error("fixed head bit accounting");for(int a=0;a<6;a++){if(a)f<<',';f<<"{\"name\":\""<<CLEAN_ARM8[a]<<"\",\"saving_bytes\":"<<gain[a]/8<<",\"prediction_FNV64\":\""<<hash[a]<<"\"}";}f<<"],\"off_head_saving_bytes\":"<<off_gain/8<<",\"scored_bits\":"<<bits<<",\"wall_seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"status\":\"FIXED_SEMANTIC_CONFIRMATION_NOT_ARCHIVE\",\"core_training\":false,\"deletions\":[]}";ofstream mg(out+".marginals",ios::binary);for(double a:marginal)mg.write(reinterpret_cast<char*>(&a),8);'''+s[end:]
s=s.replace('if(argc!=9)return 2;run_clean8(argv[1],argv[2],argv[3],argv[4],argv[5],argv[6],stoull(argv[7]),argv[8]);', 'if(argc!=10)return 2;run_clean8(argv[1],argv[2],argv[3],argv[4],argv[5],argv[6],stoull(argv[7]),argv[8],argv[9]);')
(project_path('research_round8_fixed_semantic.cpp', base=R)).write_text(s,encoding='utf-8')
