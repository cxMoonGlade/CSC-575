from pathlib import Path
from collections import defaultdict
import csv,hashlib,importlib.util,json,math,sys
ROOT=Path('/home/cx/Documents/csc475/Proj')
WORK=Path('/tmp/chordrec_root_fast')
sys.path.insert(0,str(ROOT))
from chordrec.data import reduce_label
spec=importlib.util.spec_from_file_location('reviewed_fast_figures',WORK/'figures.py')
figures=importlib.util.module_from_spec(spec);spec.loader.exec_module(figures)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=WORK/'results'; assets=WORK/'figures_final'
selection=json.loads((assets/'error_case_selection.json').read_text())
all_rows=list(csv.DictReader((run/'per_recording.csv').open()))
rows=[r for r in all_rows if r['decoder']=='viterbi' and r['method'] in ('long','projection')]
pairs={}
for row in rows:
 key=(row['recording'],row['method'])
 assert key not in pairs
 pairs[key]=row
names={r['recording'] for r in rows}
assert len(names)==64 and len(rows)==128
scoreable_names=[];chord_names=[];diffs=[]
for name in sorted(names):
 a,b=pairs[name,'projection'],pairs[name,'long']
 assert float(a['scoreable_seconds'])==float(b['scoreable_seconds'])
 assert float(a['root_scoreable_seconds'])==float(b['root_scoreable_seconds'])
 if float(a['scoreable_seconds'])>0:
  scoreable_names.append(name)
  diffs.append((float(a['duration_accuracy'])-float(b['duration_accuracy']),name))
 if float(a['root_scoreable_seconds'])>0:chord_names.append(name)
assert len(scoreable_names)==59 and len(chord_names)==58
assert sorted(set(scoreable_names)-set(chord_names))==['jazz_3']
diffs.sort()
assert [(c['delta'],c['recording']) for c in selection['cases']]==[diffs[-1],diffs[0]]
files=[]
for name in sorted(names):
 for stem in ('reference','long_viterbi','projection_viterbi'):
  path=run/'predictions'/name/f'{stem}.csv'
  fingerprint=sha(path)
  original=[(float(r['start']),float(r['end']),reduce_label(r['label'])) for r in csv.DictReader(path.open())]
  merged=figures.intervals(path)
  before=math.fsum(b-a for a,b,_ in original);after=math.fsum(b-a for a,b,_ in merged)
  mass_before=defaultdict(list);mass_after=defaultdict(list)
  for a,b,label in original:mass_before[str(label)].append(b-a)
  for a,b,label in merged:mass_after[str(label)].append(b-a)
  labels=set(mass_before)|set(mass_after)
  max_label_difference=max((abs(math.fsum(mass_before[label])-math.fsum(mass_after[label])) for label in labels),default=0.)
  assert abs(before-after)<1e-9 and max_label_difference<1e-9
  assert sha(path)==fingerprint
  files.append(dict(recording=name,track=stem,original_intervals=len(original),display_intervals=len(merged),
                    original_seconds=before,display_seconds=after,absolute_difference=abs(before-after),
                    max_label_duration_difference=max_label_difference,source_sha256=fingerprint))
selected_names={c['recording'] for c in selection['cases']}
selected=[r for r in files if r['recording'] in selected_names]
canonical=ROOT/'results/root_optimization/fast'
runner=ROOT/'experiments/root_validation/compare.py'
paths={'results_exist':canonical.exists(),'runner_exists':runner.exists()}
matched={}
if canonical.exists():
 for name in ('selection.json','input_validation.json','previous_selection.json','evaluation_plan.json'):
  p=canonical/name
  matched[name]=p.is_file() and sha(p)==sha(run/name)
  assert matched[name]
 validation=json.loads((canonical/'input_validation.json').read_text())
 assert sha(canonical/'selection.json')==validation['source_selection_sha256']
 paths['selection_binding_verified']=True
if runner.exists():
 paths['runner_matches_reviewed_source']=sha(runner)==sha(Path('/tmp/chordrec_root_progression_validation/compare.py'))
 assert paths['runner_matches_reviewed_source']
canonical_extra={}
if canonical.exists() and runner.exists():
 validation=json.loads((canonical/'input_validation.json').read_text())
 data_root=ROOT/'docs/datasets/IDMT-SMT-Guitar-fast'
 checked=0
 for record in validation['recordings']:
  for key in ('audio','annotation'):
   assert sha(data_root/record[key])==record[key+'_sha256']
   checked+=1
 assert checked==128
 for row in files:
  assert sha(canonical/'predictions'/row['recording']/(row['track']+'.csv'))==row['source_sha256']
 canonical_extra['verified_input_files']=checked
 canonical_extra['identical_saved_interval_files']=len(files)
 canonical_extra['figure_script_identical']=sha(ROOT/'experiments/root_validation/figures.py')==sha(WORK/'figures.py')
 canonical_extra['reproduction_readme_identical']=sha(ROOT/'docs/research/root_optimization/fast_validation/README.md')==sha(WORK/'README_draft.md')
 canonical_extra['session_acquirer_available']=(ROOT/'docs/research/root_optimization/fast_validation/acquire_fast.py').is_file()
 canonical_extra['figure_assets_identical']={p.name:sha(canonical/'figures'/p.name)==sha(p) for p in assets.iterdir() if p.is_file()}
 assert canonical_extra['figure_script_identical'] and canonical_extra['reproduction_readme_identical'] and canonical_extra['session_acquirer_available']
 assert all(canonical_extra['figure_assets_identical'].values())
result={'script_sha256':sha(WORK/'figures.py'),'figure_assets_sha256':{p.name:sha(p) for p in assets.iterdir() if p.is_file()},
        'recordings':64,'overall_scoreable_recordings':59,'root_scoreable_recordings':58,'n_only_piece':'jazz_3',
        'files_checked':len(files),'maximum_total_duration_difference':max(r['absolute_difference'] for r in files),
        'maximum_label_duration_difference':max(r['max_label_duration_difference'] for r in files),
        'selected_plot_tracks':selected,'selection_matches_saved_extrema':True,'source_csvs_unchanged':True,
        'canonical_path_checks':paths,'canonical_manifest_hash_matches':matched,'canonical_delivery_checks':canonical_extra,
        'visual_review':'PNG inspected at full image size: labels and titles fit; unsupported reference blocks and minor-chord hatching are distinct.',
        'inference_performed':False}
(WORK/'final_figure_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
