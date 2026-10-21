#include <array>
#include <cstdint>
#include <cstdio>
#include <limits>
#include <stdexcept>
namespace frozen {
#include "../hutter_research/probability_tables.inc"
}
#include "../hutter_research/probability_tables_packed.inc"
int main() {
  for(unsigned i=0;i<65536;i++)if(hp::kStretch[i]!=frozen::hp::kStretch[i])return 1;
  for(unsigned i=0;i<8193;i++)if(hp::kSquash[i]!=frozen::hp::kSquash[i])return 2;
  for(unsigned i=0;i<4097;i++)if(hp::kOdds[i]!=frozen::hp::kOdds[i])return 3;
  std::puts("PASS all 77826 integer values exactly match frozen tables");
  return 0;
}
