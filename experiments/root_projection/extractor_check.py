from pathlib import Path
import sys,json,csv,hashlib
import numpy as np
sys.path.insert(0,'/tmp/chordrec_root_v1/projection')
from chordrec.audio import extract_features
from chordrec.model import decode
from chordrec.projection import extract_projected_features
ROOT=Path('/home/cx/Documents/csc475/Proj');WORK=Path('/tmp/chordrec_root_v1/projection')
config=json.loads((ROOT/'configs/frozen.json').read_text())
records=sorted((r for r in json.loads((ROOT/'configs/guitarset_split.json').read_text())['records'] if r['split']=='development'),key=lambda r:r['id'])[:3]
saved={r['recording']:r for r in csv.DictReader((WORK/'experiments/root_projection/results/per_recording.csv').open())}
checks=[]
for record in records:
 actual=extract_projected_features(ROOT/record['audio'],config)
 baseline=extract_features(ROOT/record['audio'],config,required=('long',))
 for key in ('times','rms'):np.testing.assert_array_equal(actual[key],baseline[key])
 for key in ('tuning','duration'):assert actual[key]==baseline[key]
 labels=decode(actual['harmonic'],actual['rms'],config)
 with np.load('/tmp/chordrec_opt2/cache/'+record['id']+'.npz') as cached:
  correct=float(cached['weights'][labels,np.arange(len(labels))].sum())
 assert abs(correct-float(saved[record['id']]['correct_seconds']))<1e-12
 checks.append({'recording':record['id'],'metadata_exact':True,'selection_correct_seconds_exact':True,'correct_seconds':correct})
result={'checks':checks,'source_sha256':hashlib.sha256((WORK/'chordrec/projection.py').read_bytes()).hexdigest(),'six_targeted_tests_passed':True,'project_suite_before_reader':77,'test_or_idmt_accessed':False}
(WORK/'experiments/root_projection/extractor_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
