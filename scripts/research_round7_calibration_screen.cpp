// Causal final-bit calibration. Targets are consumed only AFTER prediction.
// Each policy is a normalized sequential predictor; retrospective fixed-model
// totals are diagnostics, never summed or called a transmitted-free oracle.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int M=13, BINS=64;
const std::array<double,7> temperatures{.6,.8,.9,1.,1.1,1.2,1.5};
const std::array<double,6> concentrations{4.,16.,64.,256.,1024.,4096.};

double safe(double p) { return std::clamp(p,1./65536.,65535./65536.); }
double grid(double p) {
    // Exactly preserve the neutral uint16 probability, including at extremes.
    return std::clamp(std::nearbyint(p*65536.),1.,65535.)/65536.;
}

struct Policy {
    bool confidence;
    double share;
    std::vector<std::array<double,M>> post;
    double bits=0;
    Policy(bool c,double s):confidence(c),share(s),post(c?8*BINS:8) {
        for(auto& w:post) w.fill(1./M);
    }
    void consume(int bitpos,int bin,bool correct,const std::array<double,M>& p) {
        auto& w=post[confidence?bitpos*BINS+bin:bitpos];
        double pred=0;
        for(int j=0;j<M;++j) pred+=w[j]*p[j];
        const double assigned=correct?grid(pred):1.-grid(pred);
        bits-=std::log2(assigned);
        double norm=0;
        for(int j=0;j<M;++j) { w[j]*=correct?p[j]:1.-p[j];norm+=w[j]; }
        for(auto& v:w) v=(1-share)*(v/norm)+share/M;
    }
};

int main(int argc,char**argv) {
    if(argc!=4) {std::cerr<<"usage: calibration_screen raw.bin final_p.u16 result.json\n";return 2;}
    std::ifstream raw(argv[1],std::ios::binary), tr(argv[2],std::ios::binary);
    if(!raw||!tr)throw std::runtime_error("Input open failed");
    std::vector<double> table(65536*7);
    for(int u=1;u<65536;++u) {
        double p=std::max(u,65536-u)/65536.;
        double logit=std::log(p/(1-p));
        for(int j=0;j<7;++j) table[u*7+j]=grid(safe(1/(1+std::exp(-temperatures[j]*logit))));
    }
    std::array<double,8*BINS> counts{},ones{};
    std::array<double,M> fixed{};
    std::vector<Policy> policies;
    for(bool conf:{false,true})for(double sh:{0.,1./256.,1./4096.,1./65536.})policies.emplace_back(conf,sh);
    double baseline=0,oracle=0;
    uint64_t bytes=0,bitcount=0;
    char c;
    while(raw.get(c)) {
        unsigned int byte=static_cast<unsigned char>(c);
        for(int bitpos=0;bitpos<8;++bitpos) {
            uint16_t u;
            if(!tr.read(reinterpret_cast<char*>(&u),2))throw std::runtime_error("Trace too short");
            if(!u)throw std::runtime_error("Invalid zero probability");
            const bool bit=((byte>>(7-bitpos))&1), correct=(bit==(u>=32768));
            const double base=std::max<unsigned int>(u,65536-u)/65536.;
            const int bin=std::min(BINS-1,static_cast<int>(std::log(base/(1-base))*4));
            const int ctx=bitpos*BINS+bin;
            std::array<double,M> p;
            for(int j=0;j<7;++j)p[j]=table[u*7+j];
            for(int j=0;j<6;++j)p[j+7]=grid(safe((concentrations[j]*base+ones[ctx])/(concentrations[j]+counts[ctx])));
            baseline-=std::log2(correct?base:1-base);
            double best=0;
            for(int j=0;j<M;++j){double q=correct?p[j]:1-p[j];fixed[j]-=std::log2(q);best=std::max(best,q);}
            oracle-=std::log2(best);
            for(auto& policy:policies)policy.consume(bitpos,bin,correct,p);
            counts[ctx]+=1; ones[ctx]+=correct;
            ++bitcount;
        }
        ++bytes;
    }
    char extra;
    if(tr.get(extra))throw std::runtime_error("Trace longer than raw stream");
    std::ofstream out(argv[3]);
    out<<std::setprecision(17)<<"{\n  \"raw_bytes\": "<<bytes<<",\n  \"bits_scored\": "<<bitcount
       <<",\n  \"baseline_ideal_bytes\": "<<baseline/8
       <<",\n  \"unpaid_best_expert_per_bit_ORACLE_saving_bytes\": "<<(baseline-oracle)/8
       <<",\n  \"contract\": \"strict prefix updates; quantized probabilities; ideal cost only; package and CPU excluded\",\n  \"fixed_models\": [\n";
    for(int j=0;j<M;++j) {
        out<<"    {\"type\": \""<<(j<7?"temperature":"causal_shrinkage")<<"\", \"parameter\": "
           <<(j<7?temperatures[j]:concentrations[j-7])<<", \"saving_bytes\": "<<(baseline-fixed[j])/8<<"}"<<(j<M-1?",":"")<<"\n";
    }
    out<<"  ],\n  \"policies\": [\n";
    for(size_t j=0;j<policies.size();++j) {
        auto& p=policies[j];out<<"    {\"confidence_context\": "<<(p.confidence?"true":"false")
            <<", \"share_probability\": "<<p.share<<", \"saving_bytes\": "<<(baseline-p.bits)/8
            <<", \"ideal_bytes\": "<<p.bits/8<<"}"<<(j+1<policies.size()?",":"")<<"\n";
    }
    out<<"  ]\n}\n";
    std::cout<<std::setprecision(12)<<"{\"bytes\":"<<bytes<<",\"baseline_ideal_bytes\":"<<baseline/8<<",\"policy_savings\":[";
    for(size_t j=0;j<policies.size();++j)std::cout<<(j?",":"")<<(baseline-policies[j].bits)/8;
    std::cout<<"]}\n";
}
