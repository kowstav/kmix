#pragma once

namespace hp {
inline unsigned InverseWrtByte(unsigned c) {
  if(c>=123&&c<127)c-=43;
  else if(c>=80&&c<84)c+=43;
  else if((c>=58&&c<=63)||(c>=74&&c<=79))c^=0x70;
  if(c==88||c==96)c^=88^96;
  return c;
}
// Byte-map class, not a claim to expand dictionary words or escape state.
inline unsigned PreviousWrtClass(unsigned raw) {
  unsigned b=InverseWrtByte(raw);
  if(b==' ')return 0;
  if(b=='\n')return 1;
  if(b>=128)return 2;
  if(b>='a'&&b<='z')return 3;
  if(b>='A'&&b<='Z')return 4;
  if(b>='0'&&b<='9')return 5;
  if(b<32)return 6;
  if(b=='<'||b=='>'||b=='['||b==']')return 7;
  if(b=='.'||b==','||b==';'||b==':')return 8;
  return 9;
}
}
