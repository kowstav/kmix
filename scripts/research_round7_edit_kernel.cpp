#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <vector>

extern "C" double hp_edit_logratio(const uint8_t* observed,uint64_t n,
    const uint8_t* donor,uint64_t m,const double* costs,double d,double ins,double sub) {
    const double copy=1-d-ins-sub;
    if(d<0||ins<0||sub<0||copy<0||d>=1)return std::numeric_limits<double>::quiet_NaN();
    std::vector<double> v(m+1,0),closed(m+1),next(m+1);
    v[0]=1;double gain=0;
    for(uint64_t k=0;k<n;++k) {
        const double q=std::exp2(-costs[k]);
        closed[0]=v[0];
        for(uint64_t j=1;j<=m;++j)closed[j]=v[j]+d*closed[j-1];
        std::fill(next.begin(),next.end(),0);
        for(uint64_t j=0;j<m;++j) {
            next[j]+=ins*q*closed[j];
            next[j+1]+=(sub*q+copy*(observed[k]==donor[j]))*closed[j];
        }
        next[m]+=q*closed[m];
        double z=0;for(double x:next)z+=x;
        if(z<=0)return -std::numeric_limits<double>::infinity();
        gain+=std::log2(z)+costs[k];
        for(uint64_t j=0;j<=m;++j)v[j]=next[j]/z;
    }
    return gain;
}
