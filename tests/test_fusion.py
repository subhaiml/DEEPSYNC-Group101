import numpy as np
import pytest
from consistency_fusion import fuse, correlate

def test_single_channel_attack_survives_dilution():
    for values in [(.9,.15,.15),(.15,.9,.15),(.15,.15,.9)]:
        r=fuse(*values)
        assert r['score']>.55 and r['naive_average']<.55

def test_missing_modalities_never_authenticate():
    r=fuse(.1,None,None)
    assert not r['complete'] and 'Inconclusive' in r['verdict']
    assert fuse(None,None,None)['score'] is None

def test_gate_boundary():
    assert fuse(.15,.15,.79)['gate_applied']
    assert not fuse(.15,.15,.8)['gate_applied']

def test_report_formula():
    r=fuse(.9,.2,.4)
    assert r['score']==pytest.approx(.6*.9+.4*(.4*.9+.35*.2+.25*.4))

def test_silence_and_missing_landmarks_abstain():
    assert correlate(np.ones(100),np.zeros(100))['score'] is None
    assert correlate(np.full(100,np.nan),np.ones(100))['score'] is None

def test_recovers_known_delay():
    rng=np.random.default_rng(42)
    m=np.convolve(rng.uniform(.1,1,300),np.ones(5)/5,mode='same')
    r=np.concatenate([np.zeros(4),m[:-4]])
    out=correlate(m,r)
    assert out['lag_ms']==267
    assert out['peak_correlation']>.98

def test_independent_signals_less_consistent():
    rng=np.random.default_rng(1)
    m=rng.uniform(0,1,300); r=rng.uniform(0,1,300)
    assert correlate(m,r)['score']>.5
