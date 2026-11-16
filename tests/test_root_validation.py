"""Checks for N-aware root scoring and frozen input verification."""
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
import numpy as np
import pytest
import soundfile as sf
from experiments.root_validation import compare


def test_reference_n_does_not_inflate_root_accuracy():
    reference=[(0,1,'C:maj'),(1,10,'N'),(10,12,'D:maj')]
    prediction=[(0,1,'C:min'),(1,10,'N'),(10,11,'E:maj'),(11,12,'N')]
    score=compare.score_prediction(reference,prediction,12)
    assert score['duration_accuracy']==pytest.approx(9/12)
    assert score['chord_accuracy']==0
    assert score['root_correct_seconds']==1
    assert score['root_scoreable_seconds']==3
    assert score['root_accuracy']==pytest.approx(1/3)
    assert score['other_root_seconds']==score['chord_to_n_seconds']==1
    assert score['no_chord_correct_seconds']==9


def test_only_n_reference_has_no_root_denominator():
    score=compare.score_prediction([(0,2,'N')],[(0,2,'N')],2)
    assert score['duration_accuracy']==1
    assert score['root_scoreable_seconds']==score['root_correct_seconds']==0
    assert score['root_accuracy'] is None


def test_aggregation_uses_duration_and_preserves_zero_coverage():
    first=compare.score_prediction([(0,1,'C:maj')],[(0,1,'C:min')],1)
    second=compare.score_prediction([(0,3,'D:maj')],[(0,3,'E:maj')],3)
    excluded=compare.score_prediction([(0,2,'X')],[(0,2,'N')],2)
    rows=[dict(**score,audio_seconds=duration,runtime_seconds=.1)
          for score,duration in ((first,1),(second,3),(excluded,2))]
    total=compare.aggregate(rows)
    assert total['recordings']==3 and total['scoreable_recordings']==2
    assert total['root_accuracy']==.25 and total['other_root_seconds']==3
    assert total['coverage']==pytest.approx(4/6)
    assert total['total_runtime_seconds']==pytest.approx(.3)


def test_hash_check_precedes_reference_loading(tmp_path):
    member=compare.PREFIX+'jazz/audio/jazz_1_120BPM.wav'
    audio=tmp_path/member;audio.parent.mkdir(parents=True)
    sf.write(audio,np.zeros(22050,dtype='float32'),22050)
    annotation=audio.parent.parent/'annotation/chords/jazz_1_120BPM.csv'
    annotation.parent.mkdir(parents=True)
    annotation.write_text('0.1,1.1:C\n0.9,1.2\n1,2\n1,2\n4,4\n')
    record={'piece_id':'jazz_1','archive_path':member,'file_bytes':audio.stat().st_size}
    validated={'audio':member,'annotation':str(annotation.relative_to(tmp_path)),
        'audio_sha256':compare.sha256(audio),'annotation_sha256':compare.sha256(annotation),
        'duration_seconds':1.,'reference':[[.1,.9,'C:maj']]}
    previous={'archive_path':'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/slow/jazz/audio/jazz_1_60BPM.wav'}
    checked=compare.prepare_record(tmp_path,record,validated,previous)
    assert checked['audit']['supported_chord_seconds']==pytest.approx(.8)
    annotation.write_text('invalid changed annotation')
    with pytest.raises(ValueError,match='SHA256'):
        compare.prepare_record(tmp_path,record,validated,previous)


def test_changed_decoder_configuration_is_rejected(tmp_path):
    root=PROJECT_ROOT
    paths={'long':root/'configs/frozen.json','projection':root/'configs/note_projection.json',
           'harmonic':root/'configs/note_nnls.json'}
    assert compare.check_configs(paths)['projection']['harmonic_decay']==0
    changed=compare.load_json(paths['projection']);changed['switch_penalty']=.1
    bad=tmp_path/'changed.json';bad.write_text(__import__('json').dumps(changed))
    with pytest.raises(ValueError,match='frozen shared settings'):
        compare.check_configs({**paths,'projection':bad})


def test_prospective_plan_rejects_method_drift(tmp_path):
    import json
    project=tmp_path/'project';(project/'chordrec').mkdir(parents=True)
    sources={name:'fixed '+name for name in ('audio.py','model.py','harmonic.py','projection.py','idmt.py')}
    for name,content in sources.items():(project/'chordrec'/name).write_text(content)
    paths={key:tmp_path/(key+'.json') for key in compare.METHODS}
    for key,path in paths.items():path.write_text(key)
    plan={'methods':list(compare.METHODS),'primary_candidate':'projection','order_seed':compare.SEED,
          'config_sha256':{relative:compare.sha256(paths[key]) for key,relative in
            (('long','configs/frozen.json'),('projection','configs/note_projection.json'),('harmonic','configs/note_nnls.json'))},
          'method_sha256':{name:compare.sha256(project/'chordrec'/name) for name in sources}}
    plan_path=tmp_path/'plan.json';plan_path.write_text(json.dumps(plan))
    selection={'evaluation_plan_sha256':compare.sha256(plan_path)}
    assert compare.check_plan(project,plan_path,selection,paths)['primary_candidate']=='projection'
    (project/'chordrec/model.py').write_text('modified decoder')
    with pytest.raises(ValueError,match='Method source changed'):
        compare.check_plan(project,plan_path,selection,paths)
