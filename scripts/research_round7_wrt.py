"""Exact inverse of this tree's WRT byte mapping, retaining encoded spans."""
import re
from array import array

def inverse_byte(c):
    if 123 <= c < 127: c += 80-123
    elif 80 <= c < 84: c -= 80-123
    elif 58 <= c <= 63 or 74 <= c <= 79: c ^= 0x70
    if c in (88,96): c ^= 88 ^ 96
    return c

def load_dictionary(path):
    words=re.findall(rb'[a-z]+',open(path,'rb').read())
    reverse={}
    for j, word in enumerate(words):
        if j < 80: code=bytes([128+j])
        elif j < 3920:
            k=j-80; code=bytes([208+k//80,128+k%80])
        elif j < 44880:
            k=j-3920; code=bytes([240+(k//80)//32,208+(k//80)%32,128+k%80])
        else: raise ValueError('Dictionary exceeds documented code space')
        reverse[code]=word
    return reverse

def decode_wrt(raw, dictionary, skip_header=False):
    """Return decoded bytes, per-decoded-byte encoded starts/ends, and coded header size.

    The decoded spans include case-control bytes preceding their emitted token.
    Dictionary symbols expand only to ASCII letters. A partially cut final code
    is ignored, with the caller retaining its cost outside complete word spans.
    """
    i=6 if skip_header else 0
    if skip_header and (len(raw)<6 or raw[0]!=7 or raw[5]!=7):
        raise ValueError('Expected one WRT TEXT segment header')
    output=bytearray(); starts=array('I'); ends=array('I')
    upper=False; capital=False; pending=None
    while i<len(raw):
        begin=i if pending is None else pending
        token_start=i; c=inverse_byte(raw[i]); i+=1
        if c==7: upper=True; pending=begin; continue
        if c==64: capital=True; pending=begin; continue
        if c==6: upper=False; pending=begin; continue
        if c==12:
            if i==len(raw): break
            word=bytes([inverse_byte(raw[i])]); i+=1; upper=False
        elif c>=128:
            code=[c]
            if c>207:
                if i==len(raw): break
                c=inverse_byte(raw[i]); i+=1; code.append(c)
                if c>207:
                    if i==len(raw): break
                    code.append(inverse_byte(raw[i])); i+=1
            try: word=dictionary[bytes(code)]
            except KeyError as e: raise ValueError(f'Invalid WRT code at {token_start}: {code}') from e
            if capital:
                word=word[:1].upper()+word[1:]; capital=False
            if upper: word=word.upper()
        else:
            if not (65<=c<=90 or 97<=c<=122): upper=False
            if capital or upper: c=(c-32)&255
            if capital: capital=False
            word=bytes([c])
        pending=None
        output.extend(word)
        starts.extend([begin]*len(word)); ends.extend([i]*len(word))
    return bytes(output), starts, ends, 6 if skip_header else 0

def encoded_span(starts,ends,a,b):
    if b<=a: raise ValueError('Empty decoded span')
    return int(starts[a]),int(ends[b-1])
