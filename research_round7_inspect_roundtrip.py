import pathlib
s=pathlib.Path('/root/hp/round7_lab/src/runner.cpp').read_text();lines=s.splitlines()
for key in ['LAB_RAW','Usage','int main','Decompress','--transformer','load-transformer-probs']:
    print('KEY',key)
    loc=[i for i,l in enumerate(lines) if key in l]
    for i in loc[:2]:print('\n'.join(lines[max(0,i-5):min(len(lines),i+22)]))
print('PACKAGING_LOG',pathlib.Path('/kaggle/working/hp_round7/v5_package.log').read_text()[-2200:])
