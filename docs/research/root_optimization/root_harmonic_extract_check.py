from pathlib import Path
import sys,json,hashlib
import numpy as np
import librosa,soundfile as sf
sys.path.insert(0,'/tmp/chordrec_root_v1/harmonic')
from chordrec.audio import extract_features
from chordrec.harmonic import extract_harmonic_features, fit_chroma
from chordrec.model import decode
ROOT=Path('/home/cx/Documents/csc475/Proj')
cfg=json.loads((ROOT/'configs/frozen.json').read_text())
records=[r for r in json.loads((ROOT/'configs/guitarset_split.json').read_text())['records'] if r['split']=='development']
selected=sorted(records,key=lambda r:r['id'])[:3]
rows=[]
for rec in selected:
 path=ROOT/rec['audio']; baseline=extract_features(path,cfg,required=('long',));actual=extract_harmonic_features(path,cfg,0.)
 for key in ('times','rms'):np.testing.assert_array_equal(baseline[key],actual[key])
 for key in ('duration','tuning'):assert actual[key]==baseline[key]
 with np.load('/tmp/chordrec_opt2/cache/'+rec['id']+'.npz') as f:
  for key in ('times','rms','long'):np.testing.assert_array_equal(f[key],baseline[key])
  assert actual['tuning']==float(f['tuning'])
 y,sr=sf.read(path,dtype='float32',always_2d=True);y=y.mean(axis=1)
 if sr!=cfg['sample_rate']:y=librosa.resample(y,orig_sr=sr,target_sr=cfg['sample_rate'],res_type='soxr_hq')
 mag=np.abs(librosa.stft(y,n_fft=8192,hop_length=512,window='hann',center=True,pad_mode='constant'))[:,:len(actual['times'])]
 independent,diagnostics=fit_chroma(mag,cfg,baseline['tuning'],0.)
 np.testing.assert_array_equal(independent,actual['harmonic'])
 labels=decode(actual['harmonic'],actual['rms'],cfg)
 # Forced-N frames must match the baseline's RMS rule exactly.
 base_labels=decode(baseline['long'],baseline['rms'],cfg)
 np.testing.assert_array_equal(labels==24,base_labels==24)
 rows.append({'recording':rec['id'],'frames':len(actual['times']),'baseline_cache_exact':True,'tuning_times_rms_duration_exact':True,'independent_harmonic_chroma_exact':True,'n_frames_equal':True})
source=Path('/tmp/chordrec_root_v1/harmonic/chordrec/harmonic.py')
result={'checks':rows,'test_or_idmt_accessed':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dictionary_has_cache':hasattr(__import__('chordrec.harmonic',fromlist=['note_dictionary']).note_dictionary,'cache_info')}
assert not result['dictionary_has_cache']
Path('/tmp/root_harmonic_extract_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
