from pathlib import Path
import sys,json
import numpy as np
import scipy
from scipy.optimize import nnls, lsq_linear
from scipy.signal.windows import hann
import librosa,soundfile as sf
sys.path.insert(0,'/tmp/chordrec_root_v1/harmonic')
from chordrec.harmonic import _window_response,note_dictionary,fit_chroma
ROOT=Path('/home/cx/Documents/csc475/Proj')
cfg=json.loads((ROOT/'configs/frozen.json').read_text())
N=8192;sr=22050;n=np.arange(N);window=hann(N,sym=False)
rng=np.random.default_rng(731)
offsets=np.r_[0.,1.,-1.,.01,4000.3,-3000.7,rng.uniform(-6000,6000,20)]
expected=np.asarray([np.sum(window*np.exp(-2j*np.pi*x*n/N)) for x in offsets])
actual=_window_response(offsets,N)
window_error=float(np.max(np.abs(expected-actual)))
assert window_error<1e-7
D,indices=note_dictionary(sr,N,.13,36,60,0.)
profile_checks=[]
for midi in (36,40,48,60,72,95):
 f=440*2**((midi+.13-69)/12)
 spectrum=np.abs(np.fft.rfft(np.sin(2*np.pi*f*n/sr)*window))
 error=float(np.max(np.abs(D[:,midi-36]*(N/4)-spectrum[indices])))
 assert error<1e-7
 profile_checks.append(dict(midi=midi,maximum_absolute_error=error))
expected_indices=np.flatnonzero((librosa.fft_frequencies(sr=sr,n_fft=N)>=librosa.midi_to_hz(35.5+.13)) & (librosa.fft_frequencies(sr=sr,n_fft=N)<librosa.midi_to_hz(95.5+.13)))
np.testing.assert_array_equal(indices,expected_indices)
synthetic=[]
for decay in (0.,.6,.9):
 D,ind=note_dictionary(sr,N,0.,36,60,decay)
 a=np.zeros(60);a[[12,16,19,24]]=[1,.6,.4,.3];b=D@a
 fit,res=nnls(D,b,maxiter=600)
 g=D.T@(D@fit-b)
 error=float(np.max(np.abs(fit-a)))
 assert error<1e-8 and np.min(fit)>=0
 synthetic.append(dict(decay=decay,recovery_max_absolute_error=error,residual=res,kkt_max_active_gradient=float(np.max(np.abs(g[fit>1e-10])))))
records=json.loads((ROOT/'configs/guitarset_split.json').read_text())['records']
record=next(r for r in records if r['split']=='development' and r['id']=='00_Funk1-97-C_comp')
y,sample_rate=sf.read(ROOT/record['audio'],dtype='float32',always_2d=True);y=y.mean(axis=1)
y=librosa.resample(y,orig_sr=sample_rate,target_sr=sr,res_type='soxr_hq')
mag=np.abs(librosa.stft(y,n_fft=N,hop_length=512,window='hann',center=True,pad_mode='constant'))
with np.load('/tmp/chordrec_opt2/cache/00_Funk1-97-C_comp.npz') as data:tuning=float(data['tuning'])
checks=[]
D,indices=note_dictionary(sr,N,tuning,36,60,.9)
for frame in (100,300,500):
 b=mag[indices,frame];x,res=nnls(D,b,maxiter=600);g=D.T@(D@x-b)
 scale=max(1.,np.linalg.norm(D.T@b,np.inf))
 positive=x>1e-10
 activegrad=float(np.max(np.abs(g[positive]))) if positive.any() else 0.
 inactivegradient=float(np.min(g[~positive])) if (~positive).any() else 0.
 assert np.min(x)>=0 and activegrad/scale<1e-10 and inactivegradient/scale>=-1e-10
 alternate=lsq_linear(D,b,bounds=(0.,np.inf),method='bvls',tol=1e-12,max_iter=600)
 residual_gap=float(np.linalg.norm(D@alternate.x-b)-res)
 assert abs(residual_gap)<1e-7
 checks.append(dict(frame=frame,nonzero_coefficients=int(positive.sum()),active_gradient_max=activegrad,inactive_gradient_min=inactivegradient,relative_kkt_active=activegrad/scale,alternative_residual_difference=residual_gap))
result=dict(scipy_version=scipy.__version__,hann_dft_max_absolute_error=window_error,unit_sine_profiles=profile_checks,frequency_bin_mask_exact=True,synthetic_recovery=synthetic,dev_frame_kkt=checks,source_record=record['id'],test_or_idmt_accessed=False)
Path('/tmp/root_harmonic_independent_check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
