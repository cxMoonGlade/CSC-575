"""Numerical and temporal checks for harmonic note fitting."""
import numpy as np
import soundfile as sf
from scipy.signal.windows import hann
from chordrec.audio import extract_features
from chordrec.harmonic import _window_response, note_dictionary, fit_chroma, extract_harmonic_features


def test_hann_response_matches_sampled_fft():
    n = 8192
    phase = 173.37
    signal = np.sin(2*np.pi*phase*np.arange(n)/n) * hann(n, sym=False)
    bins = np.arange(n//2+1)
    analytic = (_window_response(bins-phase,n)-_window_response(bins+phase,n))/(2j)
    np.testing.assert_allclose(analytic, np.fft.rfft(signal), atol=1e-9, rtol=1e-9)


def test_nnls_recovers_known_nonnegative_notes():
    cfg={'sample_rate':22050,'n_fft_long':8192,'midi_min':36,'n_octaves':5}
    dictionary, bins = note_dictionary(22050,8192,.04,36,60,.6)
    amplitudes=np.zeros((60,2));amplitudes[[24,28,31],0]=[.7,1.,.9];amplitudes[[26,29,33],1]=[1.,.6,.8]
    spectrum=np.zeros((4097,2));spectrum[bins]=dictionary@amplitudes
    actual,diagnostics=fit_chroma(spectrum,cfg,.04,.6)
    expected=np.zeros((12,2));np.add.at(expected,np.arange(36,96)%12,amplitudes)
    expected/=np.linalg.norm(expected,axis=0)
    np.testing.assert_allclose(actual,expected,atol=1e-10)
    assert diagnostics['relative_residual_max']<1e-10


def test_audio_grid_and_tuning_match_baseline(tmp_path):
    sr=44100
    y=.2*np.sin(2*np.pi*261.63*np.arange(44101)/sr)
    path=tmp_path/'tone.wav';sf.write(path,y,sr)
    cfg={'sample_rate':22050,'n_fft_long':8192,'hop_length':512,'midi_min':36,'n_octaves':5}
    baseline=extract_features(path,cfg,required=('long',))
    actual=extract_harmonic_features(path,cfg,.6)
    assert actual['duration']==baseline['duration']
    assert actual['tuning']==baseline['tuning']
    np.testing.assert_array_equal(actual['times'],baseline['times'])
    np.testing.assert_array_equal(actual['rms'],baseline['rms'])
    assert actual['harmonic'].shape==baseline['long'].shape
